from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import telnetlib
import subprocess
import queue
import threading
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from constants import (MIRAI_SCAN_BIN,COMPROMISED_HOST,VICTIM_HOST)
from ip_tables_service import block_ip, unblock_ip

from ddos_service import ddos_attack_service
from inject_service import start_inject_service
from scanning_service import start_scanning_service
from reset_service import reset_demo_service
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can limit it to specific domains like ["http://example.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# WebSocket client management
clients_by_endpoint = {
    "scanning": set(),
    "inject": set(),
    "ddos": set(),
}
output_queues = {
    "scanning": queue.Queue(),
    "inject": queue.Queue(),
    "ddos": queue.Queue(),
}


result_queue_inject = queue.Queue()



@app.get("/block")
async def b_ip(ip: str = Query(...)):
    try:
        output = block_ip(ip)
        print(output)
        return JSONResponse(content={"message": f"Blocked IP {ip} successfully."}, status_code=200)    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error blocking IP: {str(e)}")


@app.get("/unblock")
async def ub_ip(ip: str = Query(...)):
    try:
        unblock_ip(ip)
        return JSONResponse(content={"message": f"Unblocked {ip} successfully"}, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unblocking IP: {str(e)}")

from bot_count_service import start_telnet_session, get_bot_count_from_all_windows
from time import sleep

telnet_session_started = False
@app.get("/bot_count")
async def count_connected_bots():
    global telnet_session_started
    try:
        if not telnet_session_started:
            start_telnet_session()
            telnet_session_started = True
            sleep(12) 

        bot_count = get_bot_count_from_all_windows()
        return JSONResponse(content={"message": f"{bot_count}"}, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving bot count: {str(e)}")



@app.get("/ddos")
async def start_ddos_attack(type: str = Query(...), duration: int = Query(...), target: str = Query(...)):
    """
    This endpoint handles DDoS attack requests.
    Expects three parameters: type, duration, and target.
    """
    try:
        # # Validate parameters
        # if type not in ["SYN flood", "UDP flood", "TCP flood"]:
        #     raise HTTPException(status_code=400, detail="Invalid attack type specified.")
        
        if duration <= 0:
            raise HTTPException(status_code=400, detail="Duration must be a positive integer.")

        attack_message = threading.Thread(target=ddos_attack_service, args=(type, duration, target))
        attack_message.start()        
        return JSONResponse(content={"message": f"Started DDoS attack of type {type} on {target} for {duration} seconds."}, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating DDoS attack: {str(e)}")



@app.get("/inject")
async def start_inject(username: str = Query(...), password: str = Query(...), ip: str = Query(...)):
    """
    This endpoint handles injection requests.
    Expects three parameters: username, password, and ip.
    """
    try:
        # Start the injection execution in a separate thread
        result = await asyncio.wait_for(start_inject_service(ip, username, password), timeout=30)

        #attack_thread.start()

        # Wait for the thread to complete
        # attack_thread.join()  # Wait for the thread to finish
        
        # Get the result from the queue

        return JSONResponse(content={"message": "Successfully injected"}, status_code=200)
    except asyncio.TimeoutError as e:
        raise HTTPException(status_code=500, detail=f"Error initiating Injection: {str(e)}")


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating Injection: {str(e)}")
    
from scapy.all import sniff, TCP

SRC1 = "10.10.10.6"
SRC2 = "10.10.10.23"
DST = "10.10.10.169"
PROTOCOL = "tcp"  # Kann auch "udp" oder "icmp" sein
INTERFACE = "enp3s0"
TCP_FLAG = "S"  # Optional: "S" für SYN, "SA" für SYN-ACK

# TCP-Flag Mapping
TCP_FLAG_MAP = {
    "S": 0x02,   # SYN
    "SA": 0x12,  # SYN-ACK
    "A": 0x10,   # ACK
    "F": 0x01,   # FIN
    "R": 0x04    # RST
}

# Paket-Zähler
packet_count = 0
lock = threading.Lock()
sniffing_active = False  # Variable zur Steuerung des Sniffing-Starts

def packet_callback(packet):
    """Callback-Funktion, die aufgerufen wird, wenn ein passendes Paket erkannt wird"""
    global packet_count

    # Protokollprüfung
    if PROTOCOL == "tcp" and not packet.haslayer(TCP):
        return
    if PROTOCOL == "udp" and not packet.haslayer("UDP"):
        return
    if PROTOCOL == "icmp" and not packet.haslayer("ICMP"):
        return

    # Prüfen, ob das Paket von einer der Quell-IPs zum Ziel-Host geht
    if packet.haslayer("IP") and packet["IP"].src in [SRC1, SRC2] and packet["IP"].dst == DST:
        # Falls TCP-Flag angegeben wurde, prüfen
        if PROTOCOL == "tcp" and TCP_FLAG:
            if packet.haslayer(TCP) and packet[TCP].flags != TCP_FLAG_MAP.get(TCP_FLAG, None):
                return  # Falls das Flag nicht passt, ignorieren

        with lock:
            packet_count += 1

def start_sniffing():
    """Startet das Sniffing, wenn es noch nicht läuft"""
    global sniffing_active
    if not sniffing_active:
        sniffing_active = True
        bpf_filter = f"{PROTOCOL} and (src {SRC1} or src {SRC2}) and dst {DST}"
        print(f"Starte Paketüberwachung auf {INTERFACE} für {PROTOCOL.upper()} von {SRC1}, {SRC2} zu {DST}...")
        sniff(iface=INTERFACE, filter=bpf_filter, prn=packet_callback, store=0)

@app.websocket("/ws/packet_count")
async def count_packets(websocket: WebSocket):
    """WebSocket-Verbindung zur Live-Übertragung der Paketanzahl"""
    await websocket.accept()

    # Sniffing erst starten, wenn der erste Client verbindet
    sniffing_thread = threading.Thread(target=start_sniffing, daemon=True)
    sniffing_thread.start()

    while True:
        await asyncio.sleep(1)  # Update jede Sekunde
        with lock:
            await websocket.send_json({"packet_count": packet_count})

@app.websocket("/ws/{endpoint}")
async def start_scanning(websocket: WebSocket, endpoint: str):

    if endpoint not in clients_by_endpoint:
        await websocket.close(code=1003)  # Unsupported endpoint
        return

    await websocket.accept()
    clients_by_endpoint[endpoint].add(websocket)
    print(f"WebSocket client connected to /ws/{endpoint}")

    if endpoint == "scanning":
        threading.Thread(target=start_scanning_service, args=(endpoint,), daemon=True).start()

    try:
        while True:
            if not output_queues[endpoint].empty():
                message = output_queues[endpoint].get()
                await websocket.send_text(message)
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print(f"WebSocket client disconnected from /ws/{endpoint}")
        clients_by_endpoint[endpoint].remove(websocket)



@app.post("/reset_demo")
async def reset_demo():
    rs1,rs2 = await reset_demo_service()
    
    if rs1 == 0 and rs2 == 0:
        return {"message": "Demo system has been reset successfully"}
    
    # If rs1 is 1, meaning Mirai on .6 was not killed
    if rs1 == 1 and rs2 == 0:
        return {"message": "Mirai on 10.0.0.6 was not deleted"}

    # If rs2 is 1, meaning Mirai on .23 was not killed
    if rs1 == 0 and rs2 == 1:
        return {"message": "Mirai on 10.0.0.23 was not deleted"}

    # If both rs1 and rs2 are 1, meaning nothing was killed
    if rs1 == 1 and rs2 == 1:
        return {"message": "Mirai on both 10.0.0.6 and 10.0.0.23 were not deleted"}

    # Default failure response
    return {"message": "Demo system reset failed"}, 500






@app.on_event("startup")
async def background_tasks():
    """
    Starts background tasks for processing output queues.
    """

    os.chdir("ReadMine-Mirai-Demo-Files/")

    for endpoint in clients_by_endpoint:
        asyncio.create_task(process_output_queue(endpoint))

async def process_output_queue(endpoint):
    """
    Continuously processes the output queue for a specific endpoint.
    """
    while True:
        if not output_queues[endpoint].empty():
            message = output_queues[endpoint].get()
            # Broadcast the message to all connected WebSocket clients
            await broadcast_to_clients(endpoint, message)
        await asyncio.sleep(0.1)


async def broadcast_to_clients(endpoint, message):
    """
    Sends a message to all WebSocket clients subscribed to a specific endpoint.
    """
    clients = clients_by_endpoint.get(endpoint, set())
    if clients:
        for client in clients:
            try:
                await client.send_text(message)
            except Exception as e:
                print(f"Error sending message to {endpoint} client: {e}")
                clients.remove(client)
    else:
        print(f"No clients connected to /ws/{endpoint}")

@app.get("/")
async def get():
    """
    Serve a simple HTML page for testing.
    """
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Attack and IP Management</title>
        </head>
        <body>
            <h1>DDOS Attack Test & IP Management</h1>
            
            <!-- Buttons for testing -->
            <button onclick="connect('scanning')">Start Scanning</button>
            <button onclick="connect('inject')">Start Inject</button>
            <button onclick="connectToDdos()">Start DDoS Attack</button>

            
            <h2>IP Block/Unblock</h2>
            <label for="ipToBlock">IP to Block:</label>
            <input type="text" id="ipToBlock" placeholder="Enter IP to block" />
            <button onclick="blockIp()">Block IP</button>
            
            <br><br>
            
            <label for="ipToUnblock">IP to Unblock:</label>
            <input type="text" id="ipToUnblock" placeholder="Enter IP to unblock" />
            <button onclick="unblockIp()">Unblock IP</button>

            <br><br>

            <button onclick="resetDemo()">Reset Demo</button>

            <br><br>

            <button onclick="botCount()">Count connected bots</button>

            <!-- Script for HTTP request to start DDoS -->
            <script>
                function connect(endpoint) {
                    if (endpoint === 'scanning') {
                        console.log(`Selected endpoint: /${endpoint}`);
                        const ws = new WebSocket(`ws://localhost:8000/ws/${endpoint}`);
                    } else if (endpoint === 'inject') {
                        const username = prompt("Enter username:");
                        const password = prompt("Enter password:");
                        const ip = prompt("Enter target IP:");

                        const url = `/inject?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}&ip=${encodeURIComponent(ip)}`;

                        fetch(url)
                            .then(response => response.json())
                            .then(data => {
                                console.log("Injection started:", data);
                                alert(data.message);  // Show the confirmation message to the user
                            })
                            .catch(error => {
                                console.error("Error starting injection:", error);
                                alert("Failed to start injection. Check the console for errors.");
                            });
                    }
                }

                function botCount() {
                
                    const url = `/bot_count`;

                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            console.log("Connected Bots", data);
                            alert(data.message);  // Show the confirmation message to the user
                        })
                        .catch(error => {
                            console.error("Error starting DDoS attack:", error);
                            alert("Failed to start DDoS attack. Check the console for errors.");
                        });

                }

                // Reset Demo functionality (POST request)
                function resetDemo() {
                    fetch('/reset_demo', {
                        method: 'POST',
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log("Demo Reset:", data);
                        alert(data.message);  // Show the confirmation message to the user
                    })
                    .catch(error => {
                        console.error("Error resetting demo:", error);
                        alert("Failed to reset the demo. Check the console for errors.");
                    });
                }

                function connectToDdos() {
                    let ws;
                    const type = prompt("Enter attack type (e.g., SYN flood):", "syn");
                    const duration = prompt("Enter duration (in seconds):", "20");
                    const target = prompt("Enter target IP address (e.g., 10.10.10.20):", "10.10.10.174");

                    // Make HTTP GET request to start DDoS
                    const url = `/ddos?type=${encodeURIComponent(type)}&duration=${encodeURIComponent(duration)}&target=${encodeURIComponent(target)}`;

                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            console.log("DDoS attack started:", data);
                            alert(data.message);  // Show the confirmation message to the user

                            ws = new WebSocket(`ws://localhost:8000/ws/packet_count`);
                            ws.onmessage = function(event) {
                                console.log("Packet Count Update:", event.data);
                            };

                        })
                        .catch(error => {
                            console.error("Error starting DDoS attack:", error);
                            alert("Failed to start DDoS attack. Check the console for errors.");
                        });
                }

                function blockIp() {
                    const ip = document.getElementById("ipToBlock").value;
                    if (ip) {
                        const url = `/block?ip=${encodeURIComponent(ip)}`;

                        fetch(url)
                            .then(response => response.json())
                            .then(data => {
                                console.log("IP Blocked:", data);
                                alert(data.message);  // Show the confirmation message to the user
                            })
                            .catch(error => {
                                console.error("Error blocking IP:", error);
                                alert("Failed to block IP. Check the console for errors.");
                            });
                    } else {
                        alert("Please enter an IP to block.");
                    }
                }

                function unblockIp() {
                    const ip = document.getElementById("ipToUnblock").value;
                    if (ip) {
                        const url = `/unblock?ip=${encodeURIComponent(ip)}`;

                        fetch(url)
                            .then(response => response.json())
                            .then(data => {
                                console.log("IP Unblocked:", data);
                                alert(data.message);  // Show the confirmation message to the user
                            })
                            .catch(error => {
                                console.error("Error unblocking IP:", error);
                                alert("Failed to unblock IP. Check the console for errors.");
                            });
                    } else {
                        alert("Please enter an IP to unblock.");
                    }
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html)

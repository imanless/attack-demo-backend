import threading
from scapy.all import sniff, TCP
from constants import (COMPROMISED_HOST,VICTIM_HOST,INTERFACE)


SRC1 = COMPROMISED_HOST
SRC2 = VICTIM_HOST



TCP_FLAG_MAP = {
    "S": 0x02,
    "A": 0x10,
    "F": 0x01,
    "R": 0x04
}

packet_count = 0
lock = threading.Lock()
sniffing_active = False 

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
            packet_count += 1

def start_sniffing(protocol, destination,tcp_flag):
    """Startet das Sniffing, wenn es nicht bereits läuft"""
    global sniffing_active

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

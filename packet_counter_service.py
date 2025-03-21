import threading
from scapy.all import sniff, TCP
from constants import (COMPROMISED_HOST,VICTIM_HOST)
# Konfiguration
SRC1 = COMPROMISED_HOST
SRC2 = VICTIM_HOST
DST = "10.10.10.169"
PROTOCOL = "tcp"
INTERFACE = "enp3s0"
TCP_FLAG = "S"

# TCP-Flag Mapping
TCP_FLAG_MAP = {
    "S": 0x02,
    "SA": 0x12,
    "A": 0x10,
    "F": 0x01,
    "R": 0x04
}

# Paket-Zähler
packet_count = 0
lock = threading.Lock()
sniffing_active = False  # Steuerung des Sniffings

def packet_callback(packet):
    """Callback-Funktion für das Sniffing"""
    global packet_count

    # Protokollprüfung
    if PROTOCOL == "tcp" and not packet.haslayer(TCP):
        return
    if PROTOCOL == "udp" and not packet.haslayer("UDP"):
        return
    if PROTOCOL == "icmp" and not packet.haslayer("ICMP"):
        return

    # Prüfen, ob das Paket von den angegebenen Quellen kommt
    if packet.haslayer("IP") and packet["IP"].src in [SRC1, SRC2] and packet["IP"].dst == DST:
        if PROTOCOL == "tcp" and TCP_FLAG:
            if packet.haslayer(TCP) and packet[TCP].flags != TCP_FLAG_MAP.get(TCP_FLAG, None):
                return  # Falls das Flag nicht passt, ignorieren

        with lock:
            packet_count += 1

def start_sniffing():
    """Startet das Sniffing, wenn es nicht bereits läuft"""
    global sniffing_active
    if not sniffing_active:
        sniffing_active = True
        bpf_filter = f"{PROTOCOL} and (src {SRC1} or src {SRC2}) and dst {DST}"
        print(f"Starte Paketüberwachung auf {INTERFACE} für {PROTOCOL.upper()} von {SRC1}, {SRC2} zu {DST}...")
        sniff(iface=INTERFACE, filter=bpf_filter, prn=packet_callback, store=0)

def get_packet_count():
    """Gibt die aktuelle Anzahl der erfassten Pakete zurück"""
    with lock:
        return packet_count

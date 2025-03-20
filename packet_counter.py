from scapy.all import sniff, TCP
import argparse
import threading

# Argumente parsen
parser = argparse.ArgumentParser(description="Zählt Pakete von bestimmten IPs zu einem Zielhost basierend auf dem Protokoll und TCP-Flags.")
parser.add_argument("--src1", required=True, help="IP-Adresse des ersten sendenden Geräts")
parser.add_argument("--src2", required=True, help="IP-Adresse des zweiten sendenden Geräts")
parser.add_argument("--dst", required=True, help="IP-Adresse des Zielhosts")
parser.add_argument("--protocol", required=True, choices=["tcp", "udp", "icmp"], help="Protokoll auswählen (tcp, udp, icmp)")
parser.add_argument("--interface", required=True, help="Netzwerk-Interface zum Sniffen (z. B. eth0, wlan0)")
parser.add_argument("--tcp-flag", required=False, help="Optional: TCP-Flag filtern (z. B. S für SYN, SA für SYN-ACK)")

args = parser.parse_args()

# TCP-Flag-Mapping
tcp_flag_map = {
    "S": 0x02,   # SYN
    "SA": 0x12,  # SYN-ACK
    "A": 0x10,   # ACK
    "F": 0x01,   # FIN
    "R": 0x04    # RST
}

# Paket-Zähler
packet_count = 0
lock = threading.Lock()

def packet_callback(packet):
    global packet_count

    # Protokollprüfung
    if args.protocol == "tcp" and not packet.haslayer(TCP):
        return
    if args.protocol == "udp" and not packet.haslayer("UDP"):
        return
    if args.protocol == "icmp" and not packet.haslayer("ICMP"):
        return

    # Prüfen, ob das Paket von einer der Quell-IPs zum Ziel-Host geht
    if packet.haslayer("IP") and packet["IP"].src in [args.src1, args.src2] and packet["IP"].dst == args.dst:
        # Falls TCP-Flag angegeben wurde, prüfen
        if args.protocol == "tcp" and args.tcp_flag:
            if packet.haslayer(TCP) and packet[TCP].flags != tcp_flag_map.get(args.tcp_flag, None):
                return  # Falls das Flag nicht passt, ignorieren

        with lock:
            packet_count += 1

def print_counter():
    while True:
        with lock:
            print(f"Pakete gezählt: {packet_count}", end="\r")

# Live-Anzeige starten
threading.Thread(target=print_counter, daemon=True).start()

# Sniffing starten
bpf_filter = f"{args.protocol} and (src {args.src1} or src {args.src2}) and dst {args.dst}"
print(f"Starte Paketüberwachung auf {args.interface} für {args.protocol.upper()} von {args.src1}, {args.src2} zu {args.dst}...")

sniff(
    iface=args.interface,
    filter=bpf_filter,
    prn=packet_callback,
    store=0
)

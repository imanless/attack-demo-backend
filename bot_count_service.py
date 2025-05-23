import subprocess
import time
import re

telnet_process = None


def is_telnet_session_active():
    """Checks if a Telnet window with 'Bots Connected' is open."""
    result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
    windows = [window for window in result.stdout.split("\n") if window.strip()]
    return any("bots connected" in window.lower() for window in windows)

def start_telnet_session():
    global telnet_process
    """Start a new terminal session and connect via telnet"""
    telnet_process = subprocess.Popen(["gnome-terminal","--title=CNC Bot Count","--", "bash", "-c", "telnet localhost 23; exec bash"])
    time.sleep(0.5)  # Warte, bis das Terminal startet

    # Login über `xdotool`
    subprocess.run(["xdotool", "type", "--delay", "100", "\n"], check=True)
    time.sleep(0.5)
    subprocess.run(["xdotool", "type", "--delay", "100", "admin\n"], check=True)
    time.sleep(0.5)
    subprocess.run(["xdotool", "type", "--delay", "100", "admin\n"], check=True)
    time.sleep(1)  # Warte auf erfolgreiche Anmeldung

def get_bot_count_from_all_windows():
    """Liest alle Fensternamen aus und sucht nach 'bots connected'."""
    result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
    print("wmctrl executed!")
    windows = [window for window in result.stdout.split("\n") if window.strip()]
    print(windows)

    # Iterate over each window line
    for window in windows:
        match = re.search(r"(\d+)\sBots\sConnected", window)
        if match:
            # If a match is found, return the number of bots
            return int(match.group(1))

    # If no match is found
    return "Bot count not found."


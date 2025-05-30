#!/bin/bash

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || { echo "Failed to change to script directory"; exit 1; }

echo "[INFO] Activating virtual environment..."
source venv/bin/activate || { echo "Virtual environment not found. Please run install-dependencies.sh first."; exit 1; }

# Start Apache2
echo "Starting Apache2 service..."
sudo service apache2 start || { echo "Apache2 service failed to start"; exit 1; }

# Change directory
echo "Changing dir into ReadMine-Mirai-Demo-Files"
cd ReadMine-Mirai-Demo-Files/ || { echo "Failed to change directory"; exit 1; }

# Start cnc in a new terminal
echo "Starting cnc in a new terminal..."
gnome-terminal --title="CNC" -- bash -c "sudo ./cnc"

echo "Changing dir into attack-demo-backend"
cd ..

# Launch Backend server in a new terminal
echo "Launching Backend server in a new terminal..."
gnome-terminal --title="Backend Server" -- bash -c "source venv/bin/activate && uvicorn app:app --host 0.0.0.0 --port 8000 --reload; exec bash"

# Launch Bot Count Window in a new terminal
echo "[INFO] Launching bot count window..."
python3 -c "from bot_count_service import start_telnet_session; start_telnet_session()" || { echo "[ERROR] Failed to launch bot count window"; exit 1; }
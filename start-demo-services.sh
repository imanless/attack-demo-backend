#!/bin/bash

# Start Apache2
echo "Starting Apache2 service..."
sudo service apache2 start || { echo "Apache2 service failed to start"; exit 1; }

# Launch Backend server in a new terminal
echo "Launching Backend server in a new terminal..."
gnome-terminal --title="Backend Server" -- bash -c "cd $(pwd); uvicorn app:app --host 0.0.0.0 --port 8000 --reload; exec bash"

# Change directory
echo "Changing dir into ReadMine-Mirai-Demo-Files"
cd ReadMine-Mirai-Demo-Files/ || { echo "Failed to change directory"; exit 1; }

# Start cnc in a new terminal
echo "Starting cnc in a new terminal..."
gnome-terminal --title="CNC" -- bash -c "sudo ./cnc; exec bash"

echo "Both processes are running in separate terminals."

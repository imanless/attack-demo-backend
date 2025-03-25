#!/bin/bash


gnome-terminal -- bash -c "sshpass -p '1234' ssh root@10.10.10.1 'daemonlogger -i phy1-ap0 -o lan2'; exec bash"

# Start Apache2
echo "Starting Apache2 service..."
sudo service apache2 start || { echo "Apache2 service failed to start"; exit 1; }

# Change directory
echo "Changing dir into ReadMine-Mirai-Demo-Files"
cd ReadMine-Mirai-Demo-Files/ || { echo "Failed to change directory"; exit 1; }

# Start cnc in a new terminal
echo "Starting cnc in a new terminal..."
gnome-terminal --title="CNC" -- bash -c "sudo ./cnc; exec bash"

echo "Changing dir into attack-demo-backend"
cd ..

# Launch Backend server in a new terminal
echo "Launching Backend server in a new terminal..."

gnome-terminal --title="Backend Server" -- bash -c "uvicorn app:app --host 0.0.0.0 --port 8000 --reload; exec bash"


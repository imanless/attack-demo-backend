#!/bin/bash

gnome-terminal --title="CNC Bot Count" -- bash -c 'telnet localhost 23; exec bash' &
sleep 1

xdotool key Return

xdotool type 'admin'
xdotool key Return

xdotool type 'admin'
xdotool key Return
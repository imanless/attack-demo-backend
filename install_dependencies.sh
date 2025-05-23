#!/bin/bash

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR" || { echo "Failed to change to script directory"; exit 1; }

echo "[INFO] Checking for system dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "[INFO] Python3 is not installed. Installing..."
    sudo apt update && sudo apt install -y python3 || { echo "Failed to install Python3"; exit 1; }
fi

if ! dpkg -s python3-venv &> /dev/null; then
    echo "[INFO] python3-venv is not installed. Installing..."
    sudo apt install -y python3-venv || { echo "Failed to install python3-venv"; exit 1; }
fi

if ! dpkg -s python3-pip &> /dev/null; then
    echo "[INFO] python3-pip is not installed. Installing..."
    sudo apt install -y python3-pip || { echo "Failed to install pip"; exit 1; }
fi

if ! command -v xdotool &> /dev/null; then
    echo "[INFO] xdotool is not installed. Installing..."
    sudo apt install -y xdotool || { echo "Failed to install xdotool"; exit 1; }
fi

if ! command -v wmctrl &> /dev/null; then
    echo "[INFO] wmctrl is not installed. Installing..."
    sudo apt install -y wmctrl || { echo "Failed to install wmctrl"; exit 1; }
fi

# Setup Python virtual environment
echo "[INFO] Checking for Python virtual environment..."

if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }
fi

source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

# Ensure required Python packages are installed in the venv
MISSING_PACKAGES=()

if ! python3 -c "import websockets" &> /dev/null; then
    MISSING_PACKAGES+=("uvicorn[standard]")
fi

if ! python3 -c "import fastapi" &> /dev/null; then
    MISSING_PACKAGES+=("fastapi")
fi

if ! python3 -c "import paramiko" &> /dev/null; then
    MISSING_PACKAGES+=("paramiko")
fi

if ! python3 -c "import requests" &> /dev/null; then
    MISSING_PACKAGES+=("requests")
fi

if ! python3 -c "import scapy" &> /dev/null; then
    MISSING_PACKAGES+=("scapy")
fi

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo "[INFO] Installing missing Python packages: ${MISSING_PACKAGES[*]}"
    pip install "${MISSING_PACKAGES[@]}" || { echo "Failed to install required Python packages"; exit 1; }
else
    echo "[INFO] All required Python packages are already installed in venv"
fi

echo "[DEBUG] Active Python: $(which python3)"
echo "[DEBUG] Venv: $VIRTUAL_ENV"
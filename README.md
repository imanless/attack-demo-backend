# Attack Demo Backend

## Overview
This project provides a backend for an attack demonstration. It includes scripts to set up the necessary infrastructure, such as an Apache web server serving binaries and a CNC (Command and Control) server.

## Setup Instructions

### 1. Initial Setup on a Fresh System
If you are starting on a freshly installed system, follow these steps to prepare the environment:

1. **Set up the Mirai database:**
   ```bash
   ./cnc_db_setup.sh
   ```

2. **Install and configure the Apache web server with Mirai binaries:**
   ```bash
   ./install_apache_web_server.sh
   ```

3. **Start the necessary services:**
   ```bash
   ./start-demo-services.sh
   ```

### 2. Running the Backend on an Already Configured System
If the system has already been set up, you only need to start the demo services:

```bash
./start-demo-services.sh
```

### Important Notes
- After starting the demo services, wait until the CNC server successfully logs in before interacting with the system. Do not switch windows or terminals during this process.
- The backend can be tested locally without a frontend by visiting: [http://localhost:8000/](http://localhost:8000/).

## Verify the Setup
- Visit [http://localhost:8000/](http://localhost:8000/) to ensure the attack demo backend is running.
- Visit [http://localhost:80/bins](http://localhost:80/bins) to check if the Apache web server is serving the `bins.sh` script and Mirai binaries.

## Configuration Details
- The `constants.py` file contains static variables such as:
  - **Camera IPs**
  - **Router username and password** (used to start `daemonlogger`)
  - **CNC server credentials**
  - **Binary name** (used to upload to the first camera)
  - **Network interface** (important for packet logging to function correctly)

## Notes
- I haven't dealt with providing a full `requirements.txt` file.
- It is assumed that the host running the backend is part of a network using the `10.10.10.x` subnet.
- The host should have the static IP `10.10.10.5`.
- The hostnames `cnc.mirai.local` and `report.mirai.local` should be assigned accordingly.

---



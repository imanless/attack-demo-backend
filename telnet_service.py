import telnetlib
import requests
from requests.auth import HTTPBasicAuth
import time, re
import subprocess


from constants import (USERNAME,PASSWORD,KILL_CMD)

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

SAFE_PROCESSES = ["mDNSResponder", "tftpupload","mydlinkevent","init", "sh", "busybox", "telnetd", "nvram_daemon", "pcmcmd", "uvc_stream", "lld2d", "udhcpc"]

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
    tn.write(command.encode("utf-8") + b"\n")
    time.sleep(1)  # Give time for the command to execute
    output = tn.read_very_eager().decode("utf-8", errors="ignore")
    return output

def find_mirai_pids(output):
    """Parses the Telnet output to find the PID of mirai.mpsl."""
    return re.findall(r"/proc/(\d+)/exe -> /mirai-scan\.mpsl", output)

def find_mirai_processes(tn):
    """Finds suspicious Mirai processes by comparing to known safe processes"""
    tn.write(b"ps w\n")
    time.sleep(1)
    output = tn.read_very_eager().decode()

    mirai_pids = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) > 4:
            pid, name = parts[0], parts[4]
            if name not in SAFE_PROCESSES and re.match(r'^[a-zA-Z0-9]{10,}$', name):  # Detect weird names
                print(f"[!] Found possible Mirai process: {pid} -> {name}")
                mirai_pids.append(pid)

    return mirai_pids

def kill_processes(tn, pids):
    """Kills the identified Mirai processes"""
    for pid in pids:
        print(f"[!] Killing process {pid}")
        tn.write(f"kill -9 {pid}\n".encode())
        time.sleep(0.5)

def kill_mirai_on_bot(host):
    """Main function to detect and kill Mirai malware"""
    tn = connect_telnet(host, USERNAME, PASSWORD)
    if not tn:
        return
    
    mirai_pids = find_mirai_processes(tn)
    
    if mirai_pids:
        kill_processes(tn, mirai_pids)
    else:
        print("No Mirai processes found.")

    tn.close()
    return 0

# Support rebooting bot devices instead of killing Mirai
def reboot_bot(host):
    tn = connect_telnet(host, USERNAME, PASSWORD)
    if not tn:
        return

    print(f"[+] Sending reboot command to {host}")
    output = execute_command(tn, "reboot")

# def kill_mirai_on_bot(host):
#     tn = connect_telnet(host, USERNAME, PASSWORD)
#     if not tn:
#         return

#     print("[+] Executing ls command to find mirai process...")
#     output = execute_command(tn, "ls -l /proc/*/exe | grep mirai")
#     print("output:", output)

#     pids = find_mirai_pids(output)
#     if pids:
#         print(f"[+] Found mirai processes with PIDs: {', '.join(pids)}")
#         for pid in pids:
#             print(f"[+] Killing process {pid}...")
#             execute_command(tn, KILL_CMD.format(pid))
#             print(f"[+] Process {pid} killed successfully.")
#     else:
#         print("[-] No mirai process found.")

#     tn.close()
#     return 0 if pids else 1




def is_telnet_already_enabled(host):
    """" return True if enabled"""
    try:
        with telnetlib.Telnet(host, timeout=5) as tn:
            response = tn.read_until(b"login:", timeout=3)
            if b"login:" in response:
                print(f"[+] Telnet is enabled on {host}.")
                return True
            else:
                print(f"[+] Telnet is NOT enabled on {host}.")
                return False
    except Exception as e:
        print(f"[+] Telnet connection failed for {host}: {e}")
        return False
    


def enable_telnet(host_ip):
    url = f"http://{host_ip}/setSystemCommand"


    data = {
        "ReplySuccessPage": "home.htm",
        "ReplyErrorPage": "errradv.htm",
        "SystemCommand": "telnetd",
        "ConfigSystemCommand": "test",
    }

    response = requests.post(
        url,
        data=data,
        auth=HTTPBasicAuth(USERNAME, PASSWORD)
    )


    return response.status_code

def upload_file_to_dlink_cam(host_ip, file_path):
    url = f"http://{host_ip}/setFileUpload"


    data = {
        "ReplySuccessPage": "replyuf.htm",
        "ReplyErrorPage": "replyuf.htm",
        "FileName": f"/{file_path}",  # Destination path
        "ConfigUploadFile": "Upload File",
    }

    files = {
        "UploadFile": (f"{file_path}", open(file_path, "rb"), "text/plain"),
    }

    response = requests.post(
        url,
        data=data,
        files=files,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
    )

    return response.status_code

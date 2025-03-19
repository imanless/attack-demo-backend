import paramiko

from constants import (ROUTER_IP,ROUTER_PASSWORD,ROUTER_USERNAME)


def ssh_execute(command):
    """SSH into OpenWRT router using password authentication."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect with a password
        ssh.connect(ROUTER_IP, username=ROUTER_USERNAME, password=ROUTER_PASSWORD)
        
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        print(f"[ssh_execute]: {output}")
        ssh.close()
        
        if error:
            return f"Error: {error}"
        return output.strip()
    
    except Exception as e:
        return f"SSH Connection Error: {e}"
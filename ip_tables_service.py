from ssh_service import ssh_execute

def block_ip(ip_address):
    """Blocks a device by its IP using iptables."""
    command = f"iptables -A INPUT -s {ip_address} -j REJECT"
    print(f"[block_ip] Command to Execute: {command}")
    return ssh_execute(command)

def unblock_ip(ip_address):
    """Removes the iptables rule blocking the specified IP."""
    command = f"iptables -D INPUT -s {ip_address} -j REJECT"
    print(f"Executing: {command}")

    return ssh_execute(command)

def list_rules():
    """Lists all iptables rules."""
    command = "iptables -L --line-numbers"
    print(f"Executing: {command}")

    return ssh_execute(command)
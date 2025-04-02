import app
import subprocess
import time 

from telnet_service import reboot_bot
from constants import (VICTIM_HOST, COMPROMISED_HOST)

# Adapted this function to reboot devices instead of killing Mirai
# Refactoring/Documentation needed throughout the codebase
# Consider cases when only one device's telnet is enabled
async def reset_demo_service():
    print("[reset_demo] Resetting the demo")
    
    reboot_bot(COMPROMISED_HOST)
    reboot_bot(VICTIM_HOST)
    
    print("[reset_demo] Waiting for devices to reboot...")
    
    #Wait until devices are reachable again
    start_time = time.time()
    while True:
        ping_compromised = ping(COMPROMISED_HOST)
        ping_victim = ping(VICTIM_HOST)

        if not ping_compromised and not ping_victim:
            print("[reset_demo] Demo has been successfully reset!")
            return 0, 0
        
        time.sleep(1)


        if time.time() - start_time > 120: # Two minutes timeout
            print("[reset_demo] Timeout: device not reachable")
            return 1, 1



def ping(host):
    result = subprocess.run(
            ["ping", "-c", "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    return result.returncode

"""
async def reset_demo_service():
    
    print("[reset_demo] Resetting the demo")


    print("[reset_demo] kill mirai on bot 10.10.10.6")

    enable_telnet(COMPROMISED_HOST)
    
    resp_1 = kill_mirai_on_bot("10.10.10.6")

    if resp_1 == 0:

        print("[reset_demo] killed mirai on bot 10.10.10.6")
    else:
        print("[reset_demo] nothing killed")

    # if mirai got injected, telnet will be disabled

    enable_telnet(VICTIM_HOST)

    resp_2 = kill_mirai_on_bot("10.10.10.23")

    time.sleep(1)

    kill_process_by_pattern("telnet localhost 23")
    app.telnet_session_started = False

    return resp_1, resp_2


    # if injected:
    #     kill_process_by_pattern("loader")

    #     print("[reset_demo] kill loader on local machine")

    #     time.sleep(1)
"""

from telnet_service import *
from constants import (VICTIM_HOST,COMPROMISED_HOST)
import app
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

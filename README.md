# Attack Demo Backend

Make sure cameras are powered.

Enable port mirroring: 

1. ssh root@10.10.10.1 
2. ip link set phy1-ap0 promisc on
3. daemonlogger -i phy1-ap0 -o lan0

Connect ethernet cable to lan0 of router and to your machine's ethernet port.

execute bash file in /home/diot/Documents/diot-demo/DAC-demo/run 

./on-start-demo.sh

Visit: http://localhost:8000/ to make sure attack demo backend is running.

Launch attack demo frontend.
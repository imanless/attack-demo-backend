# Attack Demo Backend

This setup assumes that the Apache web server is installed and there is a directory on the server (localhost/bins) where a `bins.sh` script and Mirai binaries for different CPU architectures are uploaded. It is also important that the permissions of these files are set in such a way that they can be downloaded.

Make sure the cameras are powered on.

### Enable Port Mirroring on Router (Works for Touris Omnia Router, see also: [DIoT Technical Documentation](https://gitlab.trust.informatik.tu-darmstadt.de:10296/diot/diot-technical-documentation/-/blob/main/Docu-Port-Mirroring.txt?ref_type=heads))

1. SSH into the router:
   ```bash
   ssh root@10.10.10.1
2. Enable promiscuous mode on the phy1-ap0 interface:
   ```bash
   ip link set phy1-ap0 promisc on
3. Start the daemonlogger to log traffic from phy1-ap0 to lan0: 
   ```bash
   daemonlogger -i phy1-ap0 -o lan0
4. Connect the Ethernet cable from lan0 on the router to your machine's Ethernet port.


### Run the Demo

Execute the following script to start the necessary services:

```bash
./start-demo-services.sh
```

## Verify the Setup

- Visit [http://localhost:8000/](http://localhost:8000/) to make sure the attack demo backend is running.
- Visit [http://localhost:80/bins](http://localhost:80/bins) to verify that the Apache web server is accessible and serving the `bins.sh` script and Mirai binaries.


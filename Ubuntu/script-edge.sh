sudo -s #the command need root privileges to work

#checking for updates
apt-get update
# install java
apt install default-jre

#download .jar file from gihtub
curl -o edge.jar https://github.com/Lightency/Powerchain/blob/main/Ubuntu/edge.jar

# creating directory for edge
mkdir /usr/lib/edge
mv -t edge.jar /usr/lib/edge
# creating systemd service
mkdir /etc/edge.d
nano /etc/systemd/system/edge.service
echo "
[Unit]
Description=OpenEMS Edge 
After=network.target 
[Service]
User=root 
Group=root
Type=notify 
WorkingDirectory=/usr/lib/openems/edge
ExecStart=/usr/bin/java -Dfelix.cm.dir=/etc/edge.d/ -jar /usr/lib/edge/edge.jar 
SuccessExitStatus=143 
Restart=always 
RestartSec=10 
WatchdogSec=60 
[Install]
WantedBy=multi-user.target" >> edge.service
systemctl daemon-reload
systemctl restart edge --no-block ; journalctl -lfu edge

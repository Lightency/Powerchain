sudo -s #the command need root privileges to work

#checking for updates
apt-get update
# install java
apt install default-jre

#download .jar file from gihtub
curl -o backend.jar https://github.com/Lightency/Powerchain/blob/main/Ubuntu/backend.jar

# creating directory for edge
mkdir /usr/lib/openems/backend
mv -t backend.jar /usr/lib/openems/backend
# creating systemd service
mkdir /etc/openems/backend.d
nano /etc/systemd/system/openems/backend.service
echo "
[Unit]
Description=OpenEMS backend
After=network.target 
[Service]
User=root 
Group=root
Type=notify 
WorkingDirectory=/usr/lib/openems/backend
ExecStart=/usr/bin/java -Dfelix.cm.dir=/etc/openems/backend.d/ -jar /usr/lib/openems/backend/backend.jar 
SuccessExitStatus=143 
Restart=always 
RestartSec=10 
WatchdogSec=60 
[Install]
WantedBy=multi-user.target" >> backend.service
systemctl daemon-reload
systemctl restart backend --no-block ; journalctl -lfu backend

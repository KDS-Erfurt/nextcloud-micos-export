# nextcloud_micos_export
Move files from input to output folder and delete old files from output folder.

---
## Installation :pick:
```shell
apt install python3-venv -y
mkdir -p /opt/nextcloud-micos-export
python3 -m venv /opt/nextcloud-micos-export
source /opt/nextcloud-micos-export/bin/activate
pip install nextcloud-micos-export
ln /opt/nextcloud-micos-export/bin/nextcloud-micos-export /usr/bin/nextcloud-micos-export
deactivate
echo """[Unit]
Description=Move files from input to output folder and delete old files from output folder.
After=multi-user.target

[Service]
Type=simple
Restart=always
WorkingDirectory=/opt/nextcloud-micos-export
ExecStart=/opt/nextcloud-micos-export/bin/nextcloud-micos-export

[Install]
WantedBy=multi-user.target""" > /etc/systemd/system/nextcloud_micos_export.service
systemctl daemon-reload
systemctl enable nextcloud_micos_export.service
systemctl start nextcloud_micos_export.service
```

---
## Update :hourglass_flowing_sand:
```shell
source /opt/nextcloud-micos-export/bin/activate
pip install -U nextcloud-micos-export
deactivate
```

---
## Debug :gear:
```shell
systemctl stop nextcloud_micos_export.service
nextcloud-micos-export
systemctl start nextcloud_micos_export.service
```

---
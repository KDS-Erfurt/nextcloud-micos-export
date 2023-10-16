#!/bin/bash
backup_cwd=$(pwd)
cd {{ nextcloud_micos_export_dir }}
nano ./settings.json

# ask for restart if service is running
if [ $(systemctl is-active nextcloudmicosexport.service) = "active" ]; then
    # ask for restart
    read -p "Service is running. Restart now? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Restarting service..."
        sudo systemctl restart nextcloudmicosexport.service
    fi
fi
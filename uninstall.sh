#!/bin/bash

# asking if sure

echo "Are you sure you want to uninstall? (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    echo "Uninstalling..."
else
    echo "Aborting..."
    exit
fi

# stopping service if running
if systemctl is-active --quiet nextcloudmicosexport.service; then
    echo "Stopping service..."
    systemctl stop nextcloudmicosexport.service
fi

# disabling service if enabled
if systemctl is-enabled --quiet nextcloudmicosexport.service; then
    echo "Disabling service..."
    systemctl disable nextcloudmicosexport.service
fi

# removing service
echo "Removing service..."
rm /etc/systemd/system/nextcloudmicosexport.service
systemctl daemon-reload

# remove symlink
echo "Removing symlink..."
rm /usr/bin/nextcloudmicosexport

# uninstall python packages
echo "Uninstalling python packages..."
rm -rf /usr/local/lib/python3.9/dist-packages/nextcloudmicosexport*

# ask if backup settings.json
echo "Do you want to backup your settings.json? (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    echo "Backing up to ~/nextcloudmicosexport_settings.json"
    cp ./settings.json ~/nextcloudmicosexport_settings.json
else
    echo "Not backing up..."
fi

# removing files cwd
echo "Removing files..."
rm -r $(pwd)
#!/bin/bash

# asking for install directory, default: /opt/nextcloudmicosexport

echo "Please enter the directory where you want to install the script (default: /opt/nextcloudmicosexport):"
read INSTALLDIR

if [ -z "$INSTALLDIR" ]
then
    INSTALLDIR="/opt/nextcloudmicosexport"
fi

# check if directory exists, if not create it

if [ ! -d "$INSTALLDIR" ]
then
    mkdir -p $INSTALLDIR
else
    echo "Directory $INSTALLDIR already exists, do you want to overwrite it? (y/n)"
    read OVERWRITE
if [ "$OVERWRITE" == "y" ]
    then
        # check is settings.json exists, if yes, save it
        if [ -f "$INSTALLDIR/settings.json" ]
        then
            echo "Backing up settings.json to /tmp/nextcloudmicosexport_settings.json"
            cp $INSTALLDIR/settings.json /tmp/nextcloudmicosexport_settings.json
        fi

        rm -rf $INSTALLDIR
        mkdir -p $INSTALLDIR

        # restore settings.json
        if [ -f "/tmp/nextcloudmicosexport_settings.json" ]
        then
            echo "Restoring settings.json"
            cp /tmp/nextcloudmicosexport_settings.json $INSTALLDIR/settings.json
        fi
    else
        echo "Installation aborted"
        exit 1
    fi
fi

# install nano if not installed
echo "Checking if nano is installed"
if [ ! -x "$(command -v nano)" ]
then
    echo "Installing nano"
    apt install nano
fi

# install python package

pip3 install .

# copy files to install directory
echo "Copying files to $INSTALLDIR"

cp -r ./nextcloudmicosexport.sh $INSTALLDIR
chmod +x $INSTALLDIR/nextcloudmicosexport.sh
sed -i "s|{{ nextcloud_micos_export_dir }}|$INSTALLDIR|g" $INSTALLDIR/nextcloudmicosexport.sh
echo "Creating symlink to /usr/bin"
ln -s $INSTALLDIR/nextcloudmicosexport.sh /usr/bin/nextcloudmicosexport

cp -r ./nextcloudmicosexport_settings.sh $INSTALLDIR
chmod +x $INSTALLDIR/nextcloudmicosexport_settings.sh
sed -i "s|{{ nextcloud_micos_export_dir }}|$INSTALLDIR|g" $INSTALLDIR/nextcloudmicosexport_settings.sh
echo "Creating symlink to /usr/bin"
ln -s $INSTALLDIR/nextcloudmicosexport_settings.sh /usr/bin/nextcloudmicosexport_settings

# copy default settings.json to install directory if it doesn't exist
if [ ! -f "$INSTALLDIR/settings.json" ]
then
    # check if a ~/nextcloudmicosexport_settings.json exists, if yes, copy it
    if [ -f "~/nextcloudmicosexport_settings.json" ]
    then
        echo "Copying ~/nextcloudmicosexport_settings.json to $INSTALLDIR"
        cp ~/nextcloudmicosexport_settings.json $INSTALLDIR/settings.json
    else
        echo "Copying default settings.json to $INSTALLDIR"
        cp ./settings.json $INSTALLDIR
    fi
fi

# copy uninstall script to install directory
echo "Copying uninstall script to $INSTALLDIR"
cp ./uninstall.sh $INSTALLDIR
chmod +x $INSTALLDIR/uninstall.sh


# copy systemd service file to /etc/systemd/system
echo "Copying systemd service file to /etc/systemd/system"
cp ./nextcloudmicosexport.service /etc/systemd/system

# reload systemd daemon
echo "Reloading systemd daemon"
systemctl daemon-reload

# ask if user wants to edit settings.json
echo "Do you want to edit settings.json now? (y/n)"
read EDITSETTINGS
if [ "$EDITSETTINGS" == "y" ]
then
    nano $INSTALLDIR/settings.json
fi

# ask if user wants to enable and start the service
echo "Do you want to enable and start the service now? (y/n)"
read ENABLESERVICE
if [ "$ENABLESERVICE" == "y" ]
then
    systemctl enable nextcloudmicosexport
    systemctl start nextcloudmicosexport
fi

echo "Installation finished"
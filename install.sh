#!/bin/bash
# Installation instructions came from: https://iotbytes.wordpress.com/mosquitto-mqtt-broker-on-raspberry-pi/

# Import the repository package signin key
u="$USER"
path="/home/$u/MQTT"
mkdir $path
wget http://repo.mosquitto.org/debian/mosquitto-repo.gpg.key --directory-prefix=$path
sudo apt-key add ~/MQTT/mosquitto-repo.gpg.key

# Make the repository for mosquitto
sudo wget http://repo.mosquitto.org/debian/mosquitto-stretch.list --directory-prefix=/etc/apt/sources.list.d/

echo "It's recommened to update you're Raspberry Pi before installing mosquitto."
echo -n "Do you want to update Raspberry Pi? [y/n] >> "
read updt
updt=$(echo "$updt" | awk '{print tolower($0)}')

if [ "y" == "$updt" ]; then
	echo "Updating Raspberry Pi..."	
	sudo apt-get update
	echo "Done updating Raspberry Pi..."
	echo ""
fi

# Installing Pip
# Most python comes with pip but who knows, maybe pip isn't installed
echo -n "Install pip? [y/n] >> "
read pypip
pypip=$(echo "$pypip" | awk '{print tolower($0)}')

if [ "y" == "$pypip" ]; then
	echo "Installing Pip..."	
	sudo apt-get install python-pip
	echo "Done installing Pip..."
	echo ""
fi

# Installing mosquitto and paho-mqtt
echo "Installing mosquitto and paho-mqtt..."
sudo apt-get install mosquitto
echo "Done installing mosquitto..."
pip install paho-mqtt
echo "Done installing paho-mqtt..."

# Checking if mosquitto is running
echo -n "Do you want to check the status of mosquitto [y/n] >> "
read srvc
srvc=$(echo "$srvc" | awk '{print tolower($0)}')

if [ "y" == "$srvc" ]; then
	service mosquitto status
	echo ""
fi

# Seeing if Raspberry Pi is listening on port 1883
echo -n "Do you want to check if the port number is 1883 [y/n] >> "
read prt
prt=$(echo "$prt" | awk '{print tolower($0)}')

if [ "y" == "$prt" ]; then
	netstat -tln | grep 1883
	echo ""
fi

echo "Install Complete..."

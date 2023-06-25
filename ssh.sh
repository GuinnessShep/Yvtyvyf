#!/bin/bash

# Install required dependencies
sudo apt update
sudo apt install -y build-essential

# Download OpenSSH source
wget https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-9.3p1.tar.gz
tar -xf openssh-9.3p1.tar.gz
cd openssh-9.3p1

# Configure and build OpenSSH
./configure
make
sudo make install

# Check if SSH service is already running
ssh_status=$(sudo service ssh status)

if [[ $ssh_status == *"Active: active"* ]]; then
  echo "SSH service is already running."
else
  # Start SSH service
  sudo service ssh start
  echo "SSH service has been started."
fi

# Set up password for SSH connection
echo "Please enter a password for SSH connections:"
read -s ssh_password
echo "$USER:$ssh_password" | sudo chpasswd

# Get network information
public_ip=$(curl -s https://api.ipify.org)

# Print connection details
echo "============================="
echo "OpenSSH has been installed and configured."
echo "You can now connect to this computer using the following details:"
echo "Host: $public_ip"
echo "Username: $USER"
echo "Password: $ssh_password"
echo "============================="

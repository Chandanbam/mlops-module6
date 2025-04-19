#!/bin/bash

# Exit on error
set -e

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common \
    git

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create app directory
echo "Creating application directory..."
mkdir -p ~/mlops-app
cd ~/mlops-app

# Create data directories
mkdir -p data/prometheus
mkdir -p data/grafana

# Set correct permissions
sudo chown -R $USER:$USER ~/mlops-app

echo "Setup complete! Please log out and log back in for docker group changes to take effect." 
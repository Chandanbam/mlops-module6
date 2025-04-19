#!/bin/bash

# Exit on error
set -e

# Default values
EC2_HOST=${EC2_HOST:-""}
EC2_USER=${EC2_USER:-"ubuntu"}
SSH_KEY=${SSH_KEY:-""}
DOCKER_HUB_USERNAME=${DOCKER_HUB_USERNAME:-""}
VERSION=${VERSION:-"latest"}

# Check required environment variables
if [ -z "$EC2_HOST" ] || [ -z "$SSH_KEY" ] || [ -z "$DOCKER_HUB_USERNAME" ]; then
    echo "Error: Required environment variables not set"
    echo "Usage: EC2_HOST=your-ec2-host SSH_KEY=path/to/key.pem DOCKER_HUB_USERNAME=username ./deploy_aws.sh"
    exit 1
fi

# Function to run command on EC2
run_remote() {
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "$1"
}

echo "Creating deployment directory..."
run_remote "mkdir -p ~/mlops-app"

echo "Copying configuration files..."
scp -i "$SSH_KEY" docker-compose.yml "$EC2_USER@$EC2_HOST:~/mlops-app/"
scp -i "$SSH_KEY" prometheus.yml "$EC2_USER@$EC2_HOST:~/mlops-app/"
scp -i "$SSH_KEY" -r grafana "$EC2_USER@$EC2_HOST:~/mlops-app/"

echo "Creating .env file..."
cat > .env.tmp << EOF
DOCKER_HUB_USERNAME=$DOCKER_HUB_USERNAME
VERSION=$VERSION
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin
EOF

scp -i "$SSH_KEY" .env.tmp "$EC2_USER@$EC2_HOST:~/mlops-app/.env"
rm .env.tmp

echo "Pulling and starting containers..."
run_remote "cd ~/mlops-app && docker-compose pull && docker-compose up -d"

echo "Checking container status..."
run_remote "cd ~/mlops-app && docker-compose ps"

# Get the EC2 instance's public IP
PUBLIC_IP=$(run_remote "curl -s http://169.254.169.254/latest/meta-data/public-ipv4")

echo "Deployment complete! Your services are available at:"
echo "API: http://$PUBLIC_IP:8000"
echo "API Documentation: http://$PUBLIC_IP:8000/docs"
echo "Prometheus: http://$PUBLIC_IP:9090"
echo "Grafana: http://$PUBLIC_IP:3000 (admin/admin)" 
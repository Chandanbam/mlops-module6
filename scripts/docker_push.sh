#!/bin/bash

# Exit on error
set -e

# Default values
DOCKER_HUB_USERNAME=${DOCKER_HUB_USERNAME:-""}
IMAGE_NAME="mlops-diabetes"
VERSION=${VERSION:-$(git describe --tags --always)}

# Check if username is provided
if [ -z "$DOCKER_HUB_USERNAME" ]; then
    echo "Error: DOCKER_HUB_USERNAME environment variable is not set"
    echo "Usage: DOCKER_HUB_USERNAME=yourusername ./docker_push.sh"
    exit 1
fi

# Full image name
FULL_IMAGE_NAME="$DOCKER_HUB_USERNAME/$IMAGE_NAME"

echo "Building Docker image..."
docker build -t $FULL_IMAGE_NAME:latest -t $FULL_IMAGE_NAME:$VERSION .

echo "Pushing Docker image to Docker Hub..."
docker push $FULL_IMAGE_NAME:latest
docker push $FULL_IMAGE_NAME:$VERSION

echo "Successfully pushed images:"
echo "- $FULL_IMAGE_NAME:latest"
echo "- $FULL_IMAGE_NAME:$VERSION" 
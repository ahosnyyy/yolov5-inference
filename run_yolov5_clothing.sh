#!/bin/bash

CONTAINER_NAME="yolov5-inference-yolov5-inference-1"
HEALTHCHECK_URL="http://localhost:8000/health"  # Adjust if needed
MAX_RETRIES=5
SLEEP_INTERVAL=3

# Stop the container if running
if sudo docker ps -q -f name=^/${CONTAINER_NAME}$ | grep -q .; then
  echo "Stopping container $CONTAINER_NAME ..."
  sudo docker stop $CONTAINER_NAME
else
  echo "Container $CONTAINER_NAME is not running."
fi

# Start the container
echo "Starting container $CONTAINER_NAME ..."
sudo docker start $CONTAINER_NAME

# Health check loop
echo "Checking health of $CONTAINER_NAME at $HEALTHCHECK_URL ..."
retries=0
while [ $retries -lt $MAX_RETRIES ]; do
  if curl -fs $HEALTHCHECK_URL > /dev/null; then
    echo "Health check passed!"
    exit 0
  else
    echo "Health check failed. Retrying in $SLEEP_INTERVAL seconds..."
    sleep $SLEEP_INTERVAL
    retries=$((retries+1))
  fi
done

echo "Health check failed after $MAX_RETRIES attempts."
exit 1

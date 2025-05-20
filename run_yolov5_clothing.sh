#!/bin/bash

CONTAINER_NAME="yolov5-inference-yolov5-inference-1"
HEALTHCHECK_URL="http://localhost:8001/"  # Adjust if needed
MAX_RETRIES=10
SLEEP_INTERVAL=5

function health_check() {
  retries=0
  while [ $retries -lt $MAX_RETRIES ]; do
    if curl -fs $HEALTHCHECK_URL > /dev/null; then
      echo "✅ Health check passed!"
      return 0
    else
      echo "❌ Health check failed. Retrying in $SLEEP_INTERVAL seconds..."
      sleep $SLEEP_INTERVAL
      retries=$((retries+1))
    fi
  done
  return 1
}

# Check if container is running
if sudo docker ps -q -f name=^/${CONTAINER_NAME}$ | grep -q .; then
  echo "Container $CONTAINER_NAME is already running."
else
  echo "Container $CONTAINER_NAME is not running. Starting..."
  sudo docker start $CONTAINER_NAME
fi

# First health check attempt
echo "🔍 Running first health check..."
if health_check; then
  exit 0
fi

# Restart container and try health check again
echo "🔁 Health check failed after $MAX_RETRIES attempts."
echo "🔄 Restarting container $CONTAINER_NAME ..."
sudo docker stop $CONTAINER_NAME
sudo docker start $CONTAINER_NAME

# Second health check attempt
echo "🔍 Running second health check after restart..."
if health_check; then
  exit 0
else
  echo "❌ Health check still failing after restart."
  exit 1
fi
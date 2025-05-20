#!/bin/bash

REPO_URL="https://ahosny_@bitbucket.org/mahlecomfort/yolov5-inference.git"
REPO_DIR="yolov5-inference"
HEALTHCHECK_URL="http://localhost:7410/"
MAX_RETRIES=10
SLEEP_INTERVAL=5

# Clone the repo if not present
if [ ! -d "$REPO_DIR" ]; then
  echo "Cloning repo $REPO_URL ..."
  git clone "$REPO_URL"
else
  echo "Repo already cloned."
fi

# Change into repo directory
cd "$REPO_DIR" || { echo "Failed to cd into $REPO_DIR"; exit 1; }

# Build and start containers
echo "Running docker-compose up --build -d ..."
sudo docker-compose up --build -d

# Health check loop
echo "Checking health at $HEALTHCHECK_URL ..."
retries=0
while [ $retries -lt $MAX_RETRIES ]; do
  if curl -fs "$HEALTHCHECK_URL" > /dev/null; then
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
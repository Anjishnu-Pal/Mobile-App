#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="mobile-app-build"

# Build the docker image (will download base image on first run)
docker build -t "$IMAGE_NAME" .

# Run the container and execute buildozer inside it.
# Mount project and .buildozer to preserve downloaded SDK/NDK between runs.
mkdir -p $(pwd)/.buildozer

docker run --rm -it \
  --entrypoint /bin/bash \
  -v "$(pwd)":/home/project \
  -e BUILD_MODE=android \
  $IMAGE_NAME \
  -lc "cd /home/project && rm -rf /home/project/.buildozer /root/.buildozer || true && buildozer android debug"

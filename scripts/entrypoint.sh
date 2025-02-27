#!/bin/bash

set -uxo pipefail

# Install Stuff
cd /home/runner  || true
if [ ! -f ".download-zip-complete" ] ; then
    echo "[INFO] Running download-and-extract script..."
    chmod +x scripts/download-and-extract.sh
    bash scripts/download-and-extract.sh || true
fi
echo "[INFO] All started successfully!"
tail -f /dev/null

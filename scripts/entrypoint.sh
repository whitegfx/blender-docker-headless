#!/bin/bash

set -uxo pipefail

# Install Stuff
cd /home/runner  || true
SCRIPT=scripts/download-addons.sh
if [ ! -f ".download-addons-complete" ] ; then
    echo "[INFO] Running download-addons script..."
    chmod +x $SCRIPT
    bash $SCRIPT || true
fi

cd /home/runner  || true
SCRIPT=scripts/download-data-one.sh
if [ ! -f ".download-data-one-complete" ] ; then
    echo "[INFO] Running download-data-one script..."
    chmod +x $SCRIPT
    bash $SCRIPT || true
fi

cd /home/runner  || true
SCRIPT=scripts/download-data-two.sh
if [ ! -f ".download-data-two-complete" ] ; then
    echo "[INFO] Running download-data-two script..."
    chmod +x $SCRIPT
    bash $SCRIPT || true
fi

nohup filebrowser -a 0.0.0.0 -r "$FILEBROWSER_DIRECTORY" -p 8080 &

echo "[INFO] All started successfully!"
tail -f /dev/null

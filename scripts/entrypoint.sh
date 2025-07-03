#!/bin/bash

set -uxo pipefail

USR_HOME=/home/runner

## Install Stuff
#cd $USR_HOME || true
#SCRIPT=scripts/download-addons.sh
## Check if the script exists
#if [ ! -f "$SCRIPT" ]; then
#    echo "[ERROR] Script $SCRIPT does not exist."
#    exit 1
#fi
#
#if [ ! -f ".download-addons-complete" ] ; then
#    echo "[INFO] Running download-addons script..."
#    chmod +x $SCRIPT
#    # Run the script
#    bash "$SCRIPT" || {
#        echo "[ERROR] The script $SCRIPT failed to execute."
#        exit 1
#    }
#fi
#
#cd $USR_HOME || true
#SCRIPT=scripts/download-data-one.sh
## Check if the script exists
#if [ ! -f "$SCRIPT" ]; then
#    echo "[ERROR] Script $SCRIPT does not exist."
#    exit 1
#fi
#
#if [ ! -f ".download-data-one-complete" ] ; then
#    echo "[INFO] Running download-data-one script..."
#    chmod +x $SCRIPT
#    # Run the script
#    bash "$SCRIPT" || {
#        echo "[ERROR] The script $SCRIPT failed to execute."
#        exit 1
#    }
#fi
#
#cd $USR_HOME || true
#SCRIPT=scripts/download-data-two.sh
## Check if the script exists
#if [ ! -f "$SCRIPT" ]; then
#    echo "[ERROR] Script $SCRIPT does not exist."
#    exit 1
#fi
#
#if [ ! -f ".download-data-two-complete" ] ; then
#    echo "[INFO] Running download-data-two script..."
#    chmod +x $SCRIPT
#    # Run the script
#    bash "$SCRIPT" || {
#        echo "[ERROR] The script $SCRIPT failed to execute."
#        exit 1
#    }
#fi

filebrowser config init
filebrowser users add admin adminpassword --perm.admin
# --scope /home/runner
nohup filebrowser -a 0.0.0.0 -r "$FILEBROWSER_DIRECTORY" -p 8080 &

echo "[INFO] All started successfully!"
tail -f /dev/null

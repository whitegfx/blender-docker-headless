#!/bin/bash

set -uxo pipefail

TEMP_PATH="/tmp"
USR_HOME=/home/runner

if [ -n "${ADDONS_URL:-}" ]; then
  # Define variables
  ZIP_NAME="addons.zip"
  TEMP_ZIP="${TEMP_PATH}/${ZIP_NAME}"
  TEMP_EXTRACT_DIR="${TEMP_PATH}/unzip_addon_temp"

  # Extract components
  DIR=$(dirname "$TEMP_ZIP")
  FILE=$(basename "$TEMP_ZIP")

  # Download the ZIP file
  echo "[INFO] Downloading ADDONS_URL file from $ADDONS_URL..."
  aria2c -x 10 -s 10 --dir="$DIR" --out="$FILE" "$ADDONS_URL"

  rm -rf "$TEMP_EXTRACT_DIR"  # Delete the old extraction folder
  mkdir -p "$TEMP_EXTRACT_DIR"  # Recreate the folder
  unzip -o "$TEMP_ZIP" -d "$TEMP_EXTRACT_DIR" # Extract files

  if [ -n "${BLENDER_USER_SCRIPTS:-}" ]; then
    DEST_DIR=${BLENDER_USER_SCRIPTS}
    cp -r "$TEMP_EXTRACT_DIR/blender/addons/." "$DEST_DIR"/addons/ 2>/dev/null || true
  else
    echo "[WARN] BLENDER_USER_SCRIPTS environment variable not set. Skipping  file download."
  fi

  rm "$TEMP_ZIP"
  touch "${USR_HOME}/.download-addons-complete"
  echo "[INFO] Download and extraction complete!"
else
    echo "[WARN] ADDONS_URL environment variable not set. Skipping file download."
fi

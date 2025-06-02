#!/bin/bash

set -uxo pipefail

TEMP_PATH="/tmp"
USR_HOME=/home/runner

if [ -n "${DATA_TWO_URL:-}" ]; then
  # Define variables
  ZIP_NAME="data_two.zip"
  TEMP_ZIP="${TEMP_PATH}/${ZIP_NAME}"
  TEMP_EXTRACT_DIR="/tmp/unzip_data_two_temp"

  # Extract components
  DIR=$(dirname "$TEMP_ZIP")
  FILE=$(basename "$TEMP_ZIP")

  # Download the ZIP file
  echo "[INFO] Downloading DATA_URL file from $DATA_TWO_URL..."
  aria2c -x 10 -s 10 --dir="$DIR" --out="$FILE" "$DATA_TWO_URL"

  rm -rf "$TEMP_EXTRACT_DIR"  # Delete the old extraction folder
  mkdir -p "$TEMP_EXTRACT_DIR"  # Recreate the folder
  unzip -o "$TEMP_ZIP" -d "$TEMP_EXTRACT_DIR" # Extract files

  # Extract files
  unzip -o "$TEMP_ZIP" -d "$TEMP_EXTRACT_DIR"

  cp -r "$TEMP_EXTRACT_DIR/runner/." /home/runner/ 2>/dev/null || true

  rm "$TEMP_ZIP"
  touch "${USR_HOME}/.download-data-two-complete"
  echo "[INFO] Download and extraction complete!"
else
    echo "[WARN] DATA_TWO_URL environment variable not set. Skipping file download."
fi

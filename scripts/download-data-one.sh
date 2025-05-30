#!/bin/bash

set -uxo pipefail

if [ -n "${DATA_ONE_URL:-}" ]; then
  # Define variables
  TEMP_ZIP="/tmp/data_one.zip"
  TEMP_EXTRACT_DIR="/tmp/unzip_data_one_temp"

  # Download the ZIP file
  echo "[INFO] Downloading DATA_URL file from $DATA_ONE_URL..."
  wget -O "$TEMP_ZIP" "$DATA_ONE_URL"

  rm -rf "$TEMP_EXTRACT_DIR"  # Delete the old extraction folder
  mkdir -p "$TEMP_EXTRACT_DIR"  # Recreate the folder
  unzip -o "$TEMP_ZIP" -d "$TEMP_EXTRACT_DIR" # Extract files

  # Extract files
  unzip -o "$TEMP_ZIP" -d "$TEMP_EXTRACT_DIR"

  cp -r "$TEMP_EXTRACT_DIR/runner/." /home/runner/ 2>/dev/null || true

  rm "$TEMP_ZIP"
  touch /home/runner/.download-data-one-complete
  echo "[INFO] Download and extraction complete!"
else
    echo "[WARN] DATA_ONE_URL environment variable not set. Skipping file download."
fi

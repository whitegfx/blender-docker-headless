#!/bin/bash

set -uxo pipefail

if [ -n "${ADDONS_URL:-}" ]; then
  # Define variables
  TEMP_ZIP="/tmp/addons.zip"
  TEMP_EXTRACT_DIR="/tmp/unzip_addon_temp"

  # Download the ZIP file
  echo "[INFO] Downloading ADDONS_URL file from $ADDONS_URL..."
  wget -N -O "$TEMP_ZIP" "$ADDONS_URL"

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
  touch /home/runner/.download-addons-complete
  echo "[INFO] Download and extraction complete!"
else
    echo "[WARN] ADDONS_URL environment variable not set. Skipping file download."
fi

#!/bin/bash

set -uxo pipefail

if [ -n "${ZIP_URL:-}" ]; then
  # Define variables
  TEMP_ZIP="/tmp/downloaded_file.zip"
  TEMP_EXTRACT_DIR="/tmp/unzip_temp"

  # Download the ZIP file
  echo "Downloading ZIP file from $ZIP_URL..."
  wget -N -O "$TEMP_ZIP" "$ZIP_URL"

  # Extract files
  unzip -o "$TEMP_ZIP" -d "$TEMP_EXTRACT_DIR"

  cp -r "$TEMP_EXTRACT_DIR/data/runner/." /home/runner/ 2>/dev/null || true

  if [ -n "${BLENDER_USER_SCRIPTS:-}" ]; then
    DEST_DIR=${BLENDER_USER_SCRIPTS}
    cp -r "$TEMP_EXTRACT_DIR/data/blender/addons/." "$DEST_DIR"/addons/ 2>/dev/null || true
  else
    echo "[WARN] BLENDER_USER_SCRIPTS environment variable not set. Skipping  file download."
  fi

  rm "$TEMP_ZIP"

  echo "✅ Download and extraction complete! (Merged input folders)"
  touch /home/runner/.download-zip-complete
else
    echo "[WARN] ZIP_URL environment variable not set. Skipping file download."
fi

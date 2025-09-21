#!/bin/sh
set -e

# Decode the service account JSON into a temp file
if [ -n "$GCP_SA_KEY_B64" ]; then
  echo "$GCP_SA_KEY_B64" | base64 -d > /tmp/gcp-key.json
  export GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-key.json
fi

exec "$@"


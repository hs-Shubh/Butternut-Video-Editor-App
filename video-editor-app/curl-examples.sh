#!/usr/bin/env bash
set -euo pipefail

UPLOAD=$(curl -s -X POST "http://localhost:8000/upload" \
  -F "file=@data/assets/base_video.mp4" \
  -F "metadata=@demo/sample_metadata.json")
JOB_ID=$(echo "$UPLOAD" | python -c 'import sys,json; print(json.load(sys.stdin)["job_id"])')
echo "job_id=$JOB_ID"

while true; do
  STATUS=$(curl -s "http://localhost:8000/status/$JOB_ID")
  PCT=$(echo "$STATUS" | python -c 'import sys,json; print(json.load(sys.stdin)["progress_percent"])')
  echo "progress=$PCT%"
  if [ "$PCT" = "100" ]; then
    break
  fi
  sleep 2
done

curl -L -o rendered.mp4 "http://localhost:8000/result/$JOB_ID"
echo "saved rendered.mp4"

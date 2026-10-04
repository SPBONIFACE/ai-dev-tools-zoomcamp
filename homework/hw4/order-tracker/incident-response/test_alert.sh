#!/bin/bash
set -e

PORT=${1:-8001}
echo "Sending test alert to http://localhost:${PORT}/alerts..."

curl -s -X POST "http://localhost:${PORT}/alerts" \
  -H 'Content-Type: application/json' \
  -d '{
    "alerts": [
      {
        "status": "firing",
        "labels": {
          "alertname": "ResponderTest",
          "service": "sdip-backend",
          "environment": "development",
          "test": "true"
        },
        "annotations": {
          "summary": "Test notification; no incident to fix"
        }
      }
    ]
  }' | jq .

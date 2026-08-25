#!/usr/bin/env bash
# Start the app with Uvicorn ensuring the `app` package is found inside `appserver`.
# Usage: ./run.sh

set -euo pipefail

uvicorn app.main:app --app-dir appserver --host 0.0.0.0 --port 8000 --reload

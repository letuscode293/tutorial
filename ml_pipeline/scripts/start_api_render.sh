#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${PORT:-8000}"
echo "Starting GDSS2026 API on 0.0.0.0:${PORT}"
exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT}"

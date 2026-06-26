#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${PORT:-8501}"
echo "Starting GDSS2026 dashboard on 0.0.0.0:${PORT}"
echo "API URL: ${GDSS2026_API_URL:-http://127.0.0.1:8000}"

exec streamlit run dashboard/app.py \
  --server.port "${PORT}" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false

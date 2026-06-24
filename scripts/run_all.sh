#!/bin/bash
set -e
cd "$(dirname "$0")/.."

echo "Starting GDSS2026 stack (API + Django web + Streamlit)..."
docker compose up --build

#!/bin/bash
set -e
cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

pip install -q -r requirements.txt

echo "Starting API at http://127.0.0.1:8000"
echo "In another terminal: streamlit run dashboard/app.py"
exec uvicorn api.main:app --reload --host 127.0.0.1 --port 8000

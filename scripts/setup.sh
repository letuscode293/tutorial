#!/bin/bash
set -e
cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate

pip install -q -r requirements.txt
pip install -q -r gdss2026_web/requirements.txt

python scripts/train_tabular.py

cd gdss2026_web
python manage.py migrate
python manage.py load_datasets

echo ""
echo "Setup complete."
echo "  API:       ./scripts/run_api.sh"
echo "  Web app:   cd gdss2026_web && python manage.py runserver 8001"
echo "  Dashboard: streamlit run dashboard/app.py"
echo "  All (Docker): ./scripts/run_all.sh"

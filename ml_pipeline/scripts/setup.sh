#!/bin/bash
set -e
cd "$(dirname "$0")/.."
ML_ROOT="$(pwd)"
WORKSPACE_ROOT="$(dirname "$ML_ROOT")"

if [ ! -d "$WORKSPACE_ROOT/.venv" ]; then
  python3 -m venv "$WORKSPACE_ROOT/.venv"
fi
source "$WORKSPACE_ROOT/.venv/bin/activate"

pip install -q -r requirements.txt
pip install -q -r "$WORKSPACE_ROOT/data_entry/requirements.txt"

python scripts/train_tabular.py

cd "$WORKSPACE_ROOT/data_entry"
python manage.py migrate --noinput
python manage.py load_datasets

echo ""
echo "Setup complete."
echo "  API:        cd ml_pipeline && ./scripts/run_api.sh"
echo "  Data entry: cd data_entry && python manage.py runserver 8001"
echo "  Dashboard:  cd ml_pipeline && streamlit run dashboard/app.py"
echo "  Full stack: cd .. && docker compose up --build"

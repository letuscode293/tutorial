#!/usr/bin/env python3
"""Run the full GDSS2026 pipeline: export datasets → train → reload API."""
import os
import subprocess
import sys
from pathlib import Path

import requests

ML_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = ML_ROOT.parent
DATA_ENTRY_DIR = Path(os.getenv("DATA_ENTRY_ROOT", WORKSPACE_ROOT / "data_entry"))
API_RELOAD_URL = os.getenv("GDSS2026_API_URL", "http://127.0.0.1:8000") + "/reload-models"


def main() -> int:
    os.chdir(DATA_ENTRY_DIR)
    env = os.environ.copy()
    env.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    env.setdefault("ML_PIPELINE_ROOT", str(ML_ROOT))

    export = subprocess.run(
        [sys.executable, "manage.py", "export_datasets"],
        env=env,
        capture_output=True,
        text=True,
    )
    if export.returncode != 0:
        print(export.stderr or export.stdout, file=sys.stderr)
        return export.returncode
    print(export.stdout.strip())

    # Copy exported CSVs into ml_pipeline training folder
    for name in ("Crop_recommendation.csv", "Fertilizer_Prediction.csv"):
        src = DATA_ENTRY_DIR / "datasets" / name
        dst = ML_ROOT / "datasets" / name
        if src.exists():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    train = subprocess.run(
        [sys.executable, str(ML_ROOT / "scripts" / "train_tabular.py")],
        cwd=ML_ROOT,
        capture_output=True,
        text=True,
    )
    if train.returncode != 0:
        print(train.stderr or train.stdout, file=sys.stderr)
        return train.returncode
    print(train.stdout.strip())

    try:
        response = requests.post(API_RELOAD_URL, timeout=60)
        response.raise_for_status()
        print("API models reloaded.")
    except requests.RequestException as exc:
        print(f"Models trained. API reload skipped: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

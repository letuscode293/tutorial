#!/usr/bin/env python3
"""Run the full GDSS2026 pipeline: export datasets → train → reload API."""
import os
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DJANGO_DIR = ROOT / "gdss2026_web"
API_RELOAD_URL = os.getenv("GDSS2026_API_URL", "http://127.0.0.1:8000") + "/reload-models"


def main() -> int:
    os.chdir(DJANGO_DIR)
    env = os.environ.copy()
    env.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

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

    train = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "train_tabular.py")],
        cwd=ROOT,
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

# GDSS2026 ML Pipeline

Train models, serve predictions, and deploy via CI/CD.

**This is part 2 of GDSS2026.** Data entry lives in `data_entry/` (separate repo).

## Contents

| Path | Purpose |
|------|---------|
| `scripts/train_tabular.py` | Train crop + fertilizer models |
| `api/` | FastAPI `/predict/crop`, `/predict/fertilizer` |
| `dashboard/` | Streamlit farmer UI |
| `models/` | 7 serialized `.pkl` files |
| `datasets/` | Training CSVs |
| `.github/workflows/` | CI + retrain on dataset changes |

## Quick start

```bash
./scripts/setup.sh
./scripts/run_api.sh                    # http://localhost:8000/docs
streamlit run dashboard/app.py        # http://localhost:8501
```

## Full automation (with data_entry)

```bash
python scripts/automate_pipeline.py
```

Exports from `../data_entry/`, trains, reloads API.

## Docker (API + dashboard only)

```bash
docker compose up --build
```

For data entry too, run `docker compose up` from the **project root** (parent folder).

## GitHub Actions

- `ci.yml` — train + test on every push
- `retrain-models.yml` — retrain when `datasets/` changes

Data export from Render is triggered by `data_entry` repo workflow.

# GDSS2026

End-to-end ML system for crop and fertilizer recommendations.

## Structure

```
├── data_entry/     → Django web app (add/import training data)
└── ml_pipeline/    → Train models, serve API, Streamlit dashboard
```

| Directory | Purpose | GitHub repo |
|-----------|---------|-------------|
| **`data_entry/`** | PostgreSQL data entry, CSV upload/export | [GDSS2026_web](https://github.com/letuscode293/GDSS2026_web) |
| **`ml_pipeline/`** | Training, FastAPI, deployment, CI | [tutorial](https://github.com/letuscode293/tutorial) |

## Quick start

```bash
# Setup both parts
cd ml_pipeline && ./scripts/setup.sh

# Terminal 1 — API
cd ml_pipeline && ./scripts/run_api.sh

# Terminal 2 — Data entry
cd data_entry && python manage.py runserver 8001

# Terminal 3 — Dashboard
cd ml_pipeline && streamlit run dashboard/app.py

# Or everything via Docker
docker compose up --build
```

See `ml_pipeline/TUTORIAL_PIPELINE.md` for the full guide.

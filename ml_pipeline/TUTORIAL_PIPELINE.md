# GDSS2026 — ML in Production Tutorial

Teach students the **real-world ML pipeline**: train → serialize → serve → UI → automate.

## Project layout

```
GDSS2026/
├── data_entry/              # Django web app — data entry only
│   ├── data_manager/        # Models, forms, CSV import/export
│   ├── config/              # Django settings
│   ├── datasets/            # Seed + exported CSVs
│   └── manage.py
│
└── ml_pipeline/             # Train → deploy → serve
    ├── api/                   # FastAPI prediction service
    ├── dashboard/             # Streamlit UI
    ├── datasets/              # Training CSVs (canonical for models)
    ├── models/                # Serialized .pkl artifacts
    ├── scripts/               # train_tabular.py, automate_pipeline.py
    ├── tests/                 # API tests
    ├── Notebooks/             # Exploration notebook
    ├── Dockerfile
    └── docker-compose.yml     # API + dashboard only
```

| Part | Repo | Deploy target |
|------|------|---------------|
| `data_entry/` | [GDSS2026_web](https://github.com/letuscode293/GDSS2026_web) | Render |
| `ml_pipeline/` | [tutorial](https://github.com/letuscode293/tutorial) | Docker / cloud |

---

## Module 1 — Train (`ml_pipeline/`)

```bash
cd ml_pipeline
python scripts/train_tabular.py
```

---

## Module 2 — Serve (`ml_pipeline/`)

```bash
cd ml_pipeline
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

---

## Module 3 — Data entry (`data_entry/`)

```bash
cd data_entry
pip install -r requirements.txt
python manage.py migrate
python manage.py load_datasets
python manage.py runserver 8001
```

---

## Module 4 — Dashboard (`ml_pipeline/`)

```bash
cd ml_pipeline
streamlit run dashboard/app.py
```

---

## Module 5 — Full stack (Docker)

From project root:

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000/docs |
| Data entry | http://localhost:8001/ |
| Dashboard | http://localhost:8501/ |

---

## Module 6 — Automate (GitHub Actions)

**data_entry** — `retrain-from-database.yml`:
1. Export Render PostgreSQL → CSV
2. Train in `ml_pipeline/`
3. Push updated models to GitHub

**ml_pipeline** — `ci.yml` + `retrain-models.yml`:
1. Train on push
2. Run API tests

Local glue script:

```bash
cd ml_pipeline
python scripts/automate_pipeline.py
```

---

## Student checklist

- [ ] `cd ml_pipeline && ./scripts/setup.sh`
- [ ] Start API, verify `/docs`
- [ ] Start `data_entry`, add a record
- [ ] Start Streamlit dashboard
- [ ] Run GitHub Actions retrain workflow
- [ ] `docker compose up` from project root

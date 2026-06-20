# CropAI — ML in Production Tutorial

Teach students the **real-world ML pipeline**: train → serialize → serve → UI → automate.

## Pipeline stages

```
┌─────────────┐   ┌──────────────┐   ┌─────────────┐   ┌──────────────┐   ┌─────────────┐
│ 1. TRAIN    │ → │ 2. ARTIFACTS │ → │ 3. SERVE    │ → │ 4. UI        │ → │ 5. AUTOMATE │
│ Notebooks   │   │ models/      │   │ FastAPI     │   │ Streamlit    │   │ GitHub CI   │
│ + scripts   │   │ .pkl files   │   │ /predict/*  │   │ dashboard    │   │ Docker      │
└─────────────┘   └──────────────┘   └─────────────┘   └──────────────┘   └─────────────┘
```

| Stage | Student action | Automation level |
|-------|----------------|------------------|
| Train models | Run `02_recommendation_systems.ipynb` OR `python scripts/train_tabular.py` | Script is repeatable |
| Export artifacts | Models land in `models/` | Automatic on train |
| Serve | `uvicorn api.main:app` loads models once at startup | Always-on API |
| UI | Streamlit calls API (not models directly) | Separation of concerns |
| CI | GitHub Actions retrains + tests API on every push | **Automated** |

---

## Project layout

```
ML In production/
├── datasets/                 # Crop_recommendation.csv, Fertilizer_Prediction.csv
├── models/                   # 7 serialized .pkl files
├── Notebooks/                # Training notebook
├── api/                      # Production serving layer
├── dashboard/                # Farmer-facing UI
├── scripts/train_tabular.py  # Reproducible training script
├── tests/                    # Automated quality gate
├── .github/workflows/ci.yml  # Pipeline automation
├── Dockerfile
└── docker-compose.yml
```

---

## Module 1 — Train (Build)

```bash
python scripts/train_tabular.py
```

Or explore in `Notebooks/02_recommendation_systems.ipynb`.

**Teaching point:** Notebooks explore; scripts reproduce. Production teams use scripts + CI.

---

## Module 2 — Serve (Ship)

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

Open http://localhost:8000/docs

| Endpoint | Input | Output |
|----------|-------|--------|
| `GET /health` | — | Which models are loaded |
| `POST /predict/crop` | N,P,K,temp,humidity,ph,rainfall | crop + confidence |
| `POST /predict/fertilizer` | soil, crop, nutrients | fertilizer + confidence |

---

## Module 3 — UI (Deliver)

```bash
streamlit run dashboard/app.py
```

Open http://localhost:8501

---

## Module 4 — Containerize

```bash
docker compose up --build
```

---

## Module 5 — Automate

`.github/workflows/ci.yml` on every push:

1. `python scripts/train_tabular.py`
2. `pytest tests/`

---

## Student checklist

- [ ] Run `python scripts/train_tabular.py`
- [ ] Start API, verify `/docs`
- [ ] Start Streamlit, test both tabs
- [ ] Run `docker compose up`
- [ ] Push to GitHub, watch CI pass

# GDSS2026 — Full Deployment Guide

Step-by-step guide to clone, run locally, and deploy **all three services** on Render.

## Deploy everything on Render (quick overview)

You will have **3 web services** + **1 database**:

| Service | Repo | Render name | URL (example) | Purpose |
|---------|------|-------------|---------------|---------|
| **Data entry** | `GDSS2026_web` | `gdss2026-web` | `https://gdss2026-web.onrender.com` | Add training data, trigger retrain |
| **API** | `tutorial` | `gdss2026-api` | `https://gdss2026-api.onrender.com` | ML predictions (`/docs`) |
| **Dashboard** | `tutorial` | `gdss2026-dashboard` | `https://gdss2026-dashboard.onrender.com` | Submit details → get recommendations |
| **PostgreSQL** | — | `gdss2026-db` | — | Database for data entry |

### Fast path (2 blueprints)

**1. ML API + recommendation dashboard** (`tutorial` repo):

1. Push latest `tutorial` repo (includes root `render.yaml`)
2. Render → **New** → **Blueprint**
3. Connect `letuscode293/tutorial`, branch `richard`
4. Apply — creates `gdss2026-api` + `gdss2026-dashboard` automatically

**2. Data entry** (`GDSS2026_web` repo):

1. Render → **New** → **Blueprint**
2. Connect `letuscode293/GDSS2026_web`, branch `richard`
3. Apply — creates `gdss2026-web` + PostgreSQL
4. In Render dashboard, add secrets to **gdss2026-web**:
   - `GITHUB_TOKEN` = your PAT
   - `API_RELOAD_URL` = `https://gdss2026-api.onrender.com/reload-models`

**3. GitHub Secrets** on `GDSS2026_web`: `GH_PAT`, `DATABASE_URL` (external), `DJANGO_SECRET_KEY`

### Your live URLs after deploy

```
Data entry:    https://gdss2026-web.onrender.com/
API docs:      https://gdss2026-api.onrender.com/docs
Dashboard:     https://gdss2026-dashboard.onrender.com/
```

*(Replace with your actual Render hostnames from the dashboard.)*

---

```mermaid
flowchart TB
  subgraph local["Your machine"]
    DE[data_entry Django]
    ML[ml_pipeline API + dashboard]
  end

  subgraph render["Render"]
    WEB[Django web app]
    PG[(PostgreSQL)]
  end

  subgraph github["GitHub Actions"]
    WF[retrain-from-database.yml]
  end

  WEB --> PG
  WEB -->|GITHUB_TOKEN| WF
  WF -->|export DB| PG
  WF -->|train + push| MLREPO[tutorial repo]
  WF -->|push CSVs| DEREPO[GDSS2026_web repo]
```

| Part | Repo | Deployed where |
|------|------|----------------|
| Data entry | [letuscode293/GDSS2026_web](https://github.com/letuscode293/GDSS2026_web) | Render (web + PostgreSQL) |
| ML pipeline | [letuscode293/tutorial](https://github.com/letuscode293/tutorial) | GitHub Actions + local/Docker (API optional on Render) |

---

## Phase 0 — Prerequisites

Before cloning, create accounts and install tools:

1. **GitHub account** with access to both repos (or fork them to your account).
2. **Render account** — [render.com](https://render.com)
3. **Local tools:**
   - Python 3.11+
   - Git
   - Docker (optional, for full stack locally)

---

## Phase 1 — Clone both repos

The project uses **two separate repos** side by side:

```bash
# Create a workspace folder
mkdir -p ~/gdss2026 && cd ~/gdss2026

# 1) ML pipeline (tutorial repo)
git clone -b richard https://github.com/letuscode293/tutorial.git .
# This gives you ml_pipeline/, docker-compose.yml, .github/, etc.

# 2) Data entry (separate repo — must be named data_entry)
git clone -b richard https://github.com/letuscode293/GDSS2026_web.git data_entry
```

Expected layout:

```
gdss2026/
├── data_entry/          ← GDSS2026_web repo
├── ml_pipeline/         ← inside tutorial repo
├── docker-compose.yml
└── README.md
```

**If you forked the repos**, update hardcoded references:

- `data_entry/.github/workflows/retrain-from-database.yml` → change `letuscode293/tutorial` to your fork
- Render → point to your `GDSS2026_web` fork URL

---

## Phase 2 — Local setup and smoke test

Run this before any cloud deployment.

### Step 2.1 — Install and train

```bash
cd ~/gdss2026/ml_pipeline
chmod +x scripts/*.sh
./scripts/setup.sh
```

This will:

- Create a shared `.venv` in the parent folder
- Install Python deps for both parts
- Train the 7 model files
- Run Django migrations and load seed datasets

### Step 2.2 — Start all three services (3 terminals)

**Terminal 1 — API**

```bash
cd ~/gdss2026/ml_pipeline
./scripts/run_api.sh
```

Open: http://127.0.0.1:8000/docs  
Check: `GET /health` returns OK

**Terminal 2 — Data entry**

```bash
cd ~/gdss2026
source .venv/bin/activate
cd data_entry
python manage.py runserver 8001
```

Open: http://127.0.0.1:8001/

**Terminal 3 — Dashboard**

```bash
cd ~/gdss2026
source .venv/bin/activate
cd ml_pipeline
streamlit run dashboard/app.py
```

Open: http://127.0.0.1:8501/

### Step 2.3 — Test local automation

```bash
cd ~/gdss2026/ml_pipeline
source ../.venv/bin/activate
python scripts/automate_pipeline.py
```

You should see: export → train → `API models reloaded.`

**Checkpoint:** All three URLs work locally before moving to cloud.

### Alternative — Docker full stack

From the project root:

```bash
docker compose up --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000/docs |
| Data entry | http://localhost:8001/ |
| Dashboard | http://localhost:8501/ |

---

## Phase 3 — GitHub Personal Access Token (PAT)

You need one PAT for automation.

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens**
2. Create a **classic** token with:
   - `repo` (full)
   - `workflow`
3. Copy it — you will use it in two places:
   - Render env var `GITHUB_TOKEN`
   - GitHub Secret `GH_PAT` on `GDSS2026_web`

---

## Phase 4 — Render: PostgreSQL database

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. **New +** → **PostgreSQL**
3. Settings:
   - Name: e.g. `gdss-db`
   - Database: `gdss`
   - User: `gdss_user`
   - Region: Oregon (or your choice)
   - Plan: Free
4. Click **Create Database**
5. After creation, open the DB page and copy:
   - **Internal Database URL** → for Render web service
   - **External Database URL** → for GitHub Actions (required)

Keep both URLs — they are different.

---

## Phase 5 — Render: Django web app (data entry)

### Option A — Blueprint (`render.yaml`)

1. **New +** → **Blueprint**
2. Connect repo: `letuscode293/GDSS2026_web` (branch `richard`)
3. Render reads `render.yaml` and creates web + DB

### Option B — Manual web service (recommended if DB already exists)

1. **New +** → **Web Service**
2. Connect GitHub → `GDSS2026_web`, branch `richard`
3. Settings:

| Setting | Value |
|---------|-------|
| Runtime | Python 3 |
| Build Command | `bash build.sh` |
| Start Command | `bash start.sh` |
| Root Directory | *(leave blank — repo root)* |

4. **Environment variables** (Render dashboard → Environment):

```env
PYTHON_VERSION=3.11.9
DEBUG=false
AUTO_PIPELINE=false
WEB_CONCURRENCY=2
DJANGO_SECRET_KEY=<generate a long random string>

# Internal URL from Render PostgreSQL (for the web app)
DATABASE_URL=postgresql://gdss_user:PASSWORD@dpg-xxxxx-a/gdss

GITHUB_RETRAIN=true
GITHUB_TOKEN=ghp_your_pat_here
GITHUB_REPOSITORY=letuscode293/GDSS2026_web
GITHUB_REF=richard
```

5. Click **Create Web Service** and wait for deploy (~5–10 min on free tier).

### Step 5.1 — Verify Render deploy

- Open your Render URL, e.g. `https://gdss2026-web.onrender.com`
- Check health: `https://YOUR-APP.onrender.com/health/`
- Home page should show crop/fertilizer counts (seed data loaded by `build.sh`)

**If you get 500 errors:** check Render logs — usually missing migrations or wrong `DATABASE_URL`.

---

## Phase 6 — GitHub Actions secrets (data entry repo)

Go to:  
`https://github.com/letuscode293/GDSS2026_web` → **Settings** → **Secrets and variables** → **Actions**

Add these **repository secrets**:

| Secret | Value | Why |
|--------|-------|-----|
| `GH_PAT` | Your PAT (`ghp_...`) | Checkout both repos + push trained models |
| `DATABASE_URL` | **External** PostgreSQL URL | GitHub runners cannot use Render internal hostname |
| `DJANGO_SECRET_KEY` | Same as Render `DJANGO_SECRET_KEY` | Django export step in workflow |

**Important:** `DATABASE_URL` in GitHub must be the **External** URL, not internal.

---

## Phase 7 — ML pipeline GitHub Actions (tutorial repo)

The `tutorial` repo has workflows at `.github/workflows/`:

| Workflow | Trigger | What it does |
|----------|---------|--------------|
| `ci.yml` | Every push to `richard` | Train + pytest |
| `retrain-models.yml` | Dataset changes / manual | Train + commit `.pkl` files |

**No extra secrets needed** — uses the default `GITHUB_TOKEN`.

### Step 7.1 — Verify CI

1. Go to `https://github.com/letuscode293/tutorial/actions`
2. Open **GDSS2026 Pipeline CI**
3. You should see a green run after the latest push

---

## Phase 8 — Run the full automation workflow

### Step 8.1 — Manual trigger (first time)

1. Go to `https://github.com/letuscode293/GDSS2026_web/actions`
2. Click **Retrain from database**
3. **Run workflow** → branch `richard` → **Run workflow**

The workflow will:

1. Export PostgreSQL → CSV
2. Checkout `tutorial` repo
3. Train models in `ml_pipeline/`
4. Run pytest
5. Push updated `models/*.pkl` to `tutorial`
6. Push updated CSVs to `GDSS2026_web`

**Checkpoint:** Workflow finishes green. Check `tutorial` repo for a new commit with updated `.pkl` files.

### Step 8.2 — Automatic trigger from the web app

With `GITHUB_RETRAIN=true` on Render, adding a crop or fertilizer record in the Django app triggers the same workflow via `github_dispatch`.

1. Open your Render app
2. Add a new crop record
3. You should see a success message: *"GitHub Actions retrain workflow started."*
4. Watch Actions tab on `GDSS2026_web`

### Step 8.3 — Scheduled retrain

The workflow also runs daily at **06:00 UTC** (`cron: "0 6 * * *"`).

---

## Phase 9 — Deploy ML API + recommendation dashboard

Use the **Blueprint** in the root `render.yaml` of the `tutorial` repo (deploys both services).

### Step 9.1 — Blueprint deploy

1. Push the `tutorial` repo to GitHub (must include `render.yaml` at repo root)
2. Render → **New** → **Blueprint**
3. Connect `letuscode293/tutorial`, branch `richard`
4. Click **Apply**

This creates:

| Service | Start command |
|---------|---------------|
| `gdss2026-api` | `bash scripts/start_api_render.sh` |
| `gdss2026-dashboard` | `bash scripts/start_dashboard_render.sh` |

`GDSS2026_API_URL` is wired automatically from the API service hostname.

### Step 9.2 — Verify

- API health: `https://gdss2026-api.onrender.com/health`
- API docs: `https://gdss2026-api.onrender.com/docs`
- Dashboard: `https://gdss2026-dashboard.onrender.com/` — enter soil/climate → get crop/fertilizer recommendation

### Step 9.3 — Manual deploy (alternative)

If not using Blueprint, create two web services from `tutorial` repo, root dir `ml_pipeline`:

**API**

| Setting | Value |
|---------|-------|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `bash scripts/start_api_render.sh` |
| Health Check Path | `/health` |

**Dashboard**

| Setting | Value |
|---------|-------|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `bash scripts/start_dashboard_render.sh` |
| Environment | `GDSS2026_API_URL=https://gdss2026-api.onrender.com` |

### Step 9.4 — Connect data entry to API

On the **gdss2026-web** service, add:

```env
API_RELOAD_URL=https://gdss2026-api.onrender.com/reload-models
```

After GitHub Actions retrains and pushes new models, the `tutorial` repo auto-deploys the API; or call `/reload-models` manually.

---

## Phase 10 — End-to-end verification checklist

| # | Test | Expected result |
|---|------|-----------------|
| 1 | Local API `/health` | `200 OK` |
| 2 | Local data entry home | Shows record counts |
| 3 | Local Streamlit | Predictions work |
| 4 | Render data entry `/health/` | `200 OK` |
| 5 | Render API `/health` | `200 OK` |
| 6 | Render dashboard | Crop/fertilizer recommendations work |
| 7 | Add record on Render data entry | "GitHub Actions retrain workflow started" |
| 8 | `GDSS2026_web` Actions | Green **Retrain from database** run |
| 9 | `tutorial` repo | New commit with `ml_pipeline/models/*.pkl` |
| 10 | `tutorial` Actions CI | Green train + test |

---

## Environment variables reference

### Render — data entry (required)

```env
DATABASE_URL=          # internal URL
DJANGO_SECRET_KEY=
DEBUG=false
AUTO_PIPELINE=false
GITHUB_RETRAIN=true
GITHUB_TOKEN=ghp_...
GITHUB_REPOSITORY=letuscode293/GDSS2026_web
GITHUB_REF=richard
API_RELOAD_URL=https://gdss2026-api.onrender.com/reload-models
```

### Render — dashboard

```env
GDSS2026_API_URL=gdss2026-api.onrender.com   # set automatically by Blueprint
```

### GitHub Secrets — GDSS2026_web

```
GH_PAT
DATABASE_URL           # external URL
DJANGO_SECRET_KEY
```

### Render — ML API

No environment variables required. Models load from `ml_pipeline/models/`.

### Local automation (`ml_pipeline/scripts/automate_pipeline.py`)

| Variable | Required? | Default |
|----------|-----------|---------|
| `DATA_ENTRY_ROOT` | Optional | `../data_entry` |
| `GDSS2026_API_URL` | Optional | `http://127.0.0.1:8000` |

### Optional data entry variables

| Variable | When |
|----------|------|
| `API_RELOAD_URL` | API deployed and you want hot reload after local training |
| `ML_PIPELINE_ROOT` | Local/dev — path to `ml_pipeline` when training on same machine |
| `DATABASE_EXTERNAL_URL` | If `DATABASE_URL` uses Render internal hostname |
| `ALLOWED_HOSTS` | Custom domains |
| `CSRF_TRUSTED_ORIGINS` | Custom domains |
| `GITHUB_WORKFLOW_FILE` | Default: `retrain-from-database.yml` |

---

## Common issues

| Problem | Fix |
|---------|-----|
| GitHub Actions: DB connection failed | Use **External** `DATABASE_URL` in secrets, not internal |
| `GITHUB_TOKEN not set` on Render | Add `GITHUB_TOKEN=ghp_...` and `GITHUB_RETRAIN=true` |
| Workflow push fails | `GH_PAT` needs `repo` scope; branch must be `richard` |
| Render 500 on home | Run migrations — `start.sh` does this; check logs |
| Port scan timeout / no open ports | Start Command must be `bash start.sh` (not migrate-only). Check logs for `Starting gunicorn on 0.0.0.0:...` |
| Password auth failed in Actions | Wrong `DATABASE_URL` secret or expired password |
| Models not updating on API | Redeploy API or call `/reload-models` after retrain |

---

## Related docs

- [README.md](README.md) — project overview and quick start
- [ml_pipeline/TUTORIAL_PIPELINE.md](ml_pipeline/TUTORIAL_PIPELINE.md) — ML pipeline modules for students
- [data_entry/README.md](data_entry/README.md) — data entry app specifics

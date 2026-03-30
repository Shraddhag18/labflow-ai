# LabFlow AI

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat&logo=openai&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Railway](https://img.shields.io/badge/Deployed-Railway-0B0D0E?style=flat&logo=railway&logoColor=white)

**AI-powered research workflow automation.** Paste any research log — LabFlow summarizes it, extracts findings, classifies the domain, compares studies, and generates reports using GPT-4o-mini. An agentic chat interface lets you describe what you need in plain English and the AI automatically picks and chains the right tools.

---

## 🔗 Live Links

| | |
|---|---|
| **Live Dashboard** | https://labflow-dashboard-production.up.railway.app |
| **Landing Page** | https://shraddhag18.github.io/labflow-ai/ |
| **GitHub Repo** | https://github.com/Shraddhag18/labflow-ai |
| **API Docs (Swagger)** | `<your-api-url>/docs` — available once API is running |

---

## What It Does

Research teams deal with large volumes of experiment logs, notes, and findings that are time-consuming to process manually. LabFlow AI automates the most repetitive parts:

| Workflow | What it does |
|---|---|
| **Summarize Log** | Extracts objectives, methods, results, and next steps into a clean structured summary |
| **Extract Findings** | Pulls out discoveries, hypotheses, and conclusions with confidence ratings |
| **Classify Domain** | Identifies the scientific field, subfield, and relevant tags |
| **Compare Studies** | Side-by-side comparison of two logs — agreements, differences, contradictions |
| **Generate Report** | Turns multiple summaries into a single executive research report |
| **Search Logs** | Finds the most relevant passages across your log library for a given query |

Plus an **AI Assistant** (agentic mode) where you describe your task in plain English — it picks and chains tools automatically using OpenAI's tool-calling API.

---

## Architecture

```
User (Browser)
     │
     ▼
┌─────────────────┐      HTTP/REST      ┌──────────────────────────┐
│  Streamlit      │ ──────────────────► │  FastAPI Backend          │
│  Dashboard      │                     │                           │
│  (port 8501)    │ ◄────────────────── │  /api/v1/workflows/run    │
└─────────────────┘      JSON           │  /api/v1/workflows/agent  │
                                        │  /api/v1/logs/            │
                                        │  /api/v1/analytics/       │
                                        └───────────┬──────────────┘
                                                    │
                                         ┌──────────▼──────────┐
                                         │  Agent Core          │
                                         │  (OpenAI Tool Call)  │
                                         │                      │
                                         │  PromptManager A/B   │
                                         │  6 workflow tools    │
                                         └──────────┬──────────┘
                                                    │
                              ┌─────────────────────▼─────────────────────┐
                              │  SQLAlchemy ORM                            │
                              │  SQLite (dev)  ──►  PostgreSQL (prod)      │
                              └───────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **LLM** | OpenAI GPT-4o-mini | Tool calling, summarization, extraction |
| **API** | FastAPI + Uvicorn | REST backend, async request handling |
| **Production Server** | Gunicorn + UvicornWorker | Multi-worker ASGI production server |
| **Dashboard** | Streamlit | Single-page analytics & workflow UI |
| **ORM** | SQLAlchemy 2.0 | Database models, CRUD operations |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Run history, logs, A/B results |
| **Config** | Pydantic Settings | Environment variable validation |
| **Deployment** | Railway | Cloud hosting (API + Dashboard) |
| **Landing Page** | GitHub Pages | Static marketing page |

---

## Quick Start

### 1. Clone and install

```bash
git clone https://github.com/Shraddhag18/labflow-ai.git
cd labflow-ai
pip install -r requirements.txt
```

### 2. Set up environment

```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

Open `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-key-here
```

Get a key at: https://platform.openai.com/api-keys

### 3. Start the app

```bash
python run.py
```

This starts both services in parallel:
- **API** → http://localhost:8000 (interactive docs at http://localhost:8000/docs)
- **Dashboard** → http://localhost:8501

### 4. Load sample data (optional)

```bash
python seed.py
```

Seeds 5 research logs and 30 synthetic run records so the Analytics and A/B pages show meaningful data right away.

---

## How to Use

### Option A — Paste a research log from the internet

1. Go to [PubMed](https://pubmed.ncbi.nlm.nih.gov), [arXiv](https://arxiv.org), or [bioRxiv](https://biorxiv.org)
2. Open any paper — copy the Abstract + Methods + Results text
3. In the dashboard, click **Analyze Research → Summarize a Log** and paste it
4. Or use the **AI Assistant** and type: `"Summarize this and tell me the domain"` with the log pasted in the context panel

### Option B — Use the included sample log

The repo includes a ready-to-use research log at `data/sample_logs/log_001.txt`:

```
Research Log — Enzyme Kinetics Study
Date: 2025-01-14
Researcher: Dr. A. Chen
Team: Biology

Objective:
Investigate the effect of temperature on the catalytic efficiency of lactase enzyme.

Results:
- At 37°C, Vmax = 142 µmol/min/mg (highest efficiency)
- At 50°C, enzyme denaturation observed above 45°C
- Activation energy = 48 kJ/mol between 25–37°C
...
```

Copy and paste it into any workflow to see a live AI response.

---

## API Reference

Full interactive Swagger docs: `http://localhost:8000/docs`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check — verifies DB connectivity |
| `GET` | `/api/v1/workflows/` | List all 6 available workflows |
| `POST` | `/api/v1/workflows/run` | Run a specific workflow with a payload |
| `POST` | `/api/v1/workflows/agent` | Agentic chat — model picks and chains tools |
| `POST` | `/api/v1/logs/` | Upload a new research log |
| `GET` | `/api/v1/logs/` | List all stored logs |
| `GET` | `/api/v1/analytics/metrics` | Aggregated run metrics |
| `GET` | `/api/v1/analytics/ab-results` | A/B prompt testing results per workflow |
| `GET` | `/api/v1/analytics/runs` | Full run history with latency + quality scores |

**Example request:**
```bash
curl -X POST http://localhost:8000/api/v1/workflows/run \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "log_summarizer",
    "payload": { "log_text": "Date: Jan 2025\nObjective: test enzyme stability..." }
  }'
```

---

## A/B Prompt Testing

Every workflow has two prompt variants tested in parallel:

| Variant | Approach | Avg Quality Score |
|---|---|---|
| **A — Baseline** | Simple, direct instruction to the model | ~62% |
| **B — Optimized** | Chain-of-thought reasoning + strict JSON output rules | ~85% |

**Result: Variant B achieves ~38% quality improvement on average.**

Variant assignment is deterministic per session using an MD5 hash of the input — so the same input always gets the same variant, enabling consistent A/B measurement. Results are tracked in the database and visible in the **Prompt A/B Results** page.

---

## Project Structure

```
labflow-ai/
│
├── api/                    # FastAPI application
│   ├── main.py             # App factory, middleware, lifespan
│   ├── middleware.py        # API key auth + request logging
│   ├── routers/
│   │   ├── workflows.py    # /run and /agent endpoints
│   │   ├── logs.py         # Log CRUD endpoints
│   │   └── analytics.py    # Metrics and A/B results
│   └── schemas/
│       └── schemas.py      # Pydantic request/response models
│
├── agent/                  # OpenAI tool-calling agent
│   ├── core.py             # Agentic loop (up to 5 iterations)
│   ├── tool_registry.py    # Tool definitions for OpenAI
│   ├── tools/              # 6 workflow tool implementations
│   └── prompts/
│       ├── variants.py     # Variant A and B prompts per workflow
│       └── prompt_manager.py  # MD5-based A/B selector
│
├── db/                     # Database layer
│   ├── models.py           # SQLAlchemy ORM models
│   ├── crud.py             # Create/read operations
│   └── database.py         # Engine + session factory
│
├── dashboard/
│   ├── app.py              # Single-page Streamlit app (all 5 views)
│   └── style.py            # Shared CSS
│
├── data/
│   └── sample_logs/        # Example research logs for testing
│
├── config.py               # Pydantic Settings (reads .env)
├── run.py                  # Local dev: starts API + Dashboard
├── start.py                # Railway: reads $PORT and starts service
├── seed.py                 # Seeds sample data into the database
├── requirements.txt
├── .env.example            # Copy to .env and fill in your keys
│
├── Procfile                # Railway API start command
├── railway.toml            # Railway build + health check config
├── nixpacks.toml           # Railway Nixpacks builder config
│
├── docker-compose.yml      # Local Docker dev (API + Dashboard + Postgres)
├── Dockerfile              # API container
├── Dockerfile.dashboard    # Dashboard container
│
├── render.yaml             # Alternative: deploy to Render.com
└── index.html              # GitHub Pages landing page
```

---

## Deployment

### Railway (current — production)

The app runs as two separate Railway services from the same repo:

**API service:**
- Build: Nixpacks (auto-detects Python)
- Start: `Procfile` → `gunicorn api.main:app --worker-class uvicorn.workers.UvicornWorker`
- Required env vars: `OPENAI_API_KEY`, `DATABASE_URL`, `ENVIRONMENT=production`, `API_SECRET_KEY`

**Dashboard service:**
- Start command (set manually in Railway Settings): `python start.py dashboard`
- Required env vars: `API_BASE_URL=<your-api-service-url>`, `API_SECRET_KEY`

### Render (alternative)

A `render.yaml` blueprint is included. Connect your repo at https://dashboard.render.com/new/blueprint — it provisions a PostgreSQL database and both services automatically.

### Docker (local)

```bash
docker-compose up --build
```

Starts API, Dashboard, and a PostgreSQL container locally.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | Your OpenAI API key |
| `DATABASE_URL` | No | `sqlite:///./data/labflow.db` | Postgres URL in production |
| `ENVIRONMENT` | No | `development` | `development` or `production` |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | OpenAI model to use |
| `API_BASE_URL` | No | `http://localhost:8000` | Base URL the dashboard calls |
| `API_SECRET_KEY` | No | *(empty = auth disabled)* | Secret for `X-API-Key` header |
| `AB_TEST_ENABLED` | No | `true` | Toggle A/B prompt testing |
| `LOG_LEVEL` | No | `info` | Logging verbosity |

---

## License

MIT — free to use, modify, and deploy.

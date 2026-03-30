# LabFlow AI

Agentic research assistant that automates 6 repetitive LLM-powered research workflows via a FastAPI backend and Streamlit analytics dashboard.

**Stack:** Python · FastAPI · OpenAI API · PostgreSQL (SQLite locally) · Streamlit

---

## Features

- **6 Research Workflows** automated via OpenAI tool calling:
  - `log_summarizer` — Structured summary (objectives, methods, results, next steps)
  - `findings_extractor` — Key findings, hypotheses, conclusions with confidence scores
  - `domain_classifier` — Scientific domain/subdomain classification with tags
  - `log_comparator` — Side-by-side comparison of two research logs
  - `report_generator` — Executive summary report from multiple summaries
  - `knowledge_searcher` — Semantic search across research log corpus
- **Agentic mode** — Chat interface where the model autonomously selects and chains tools
- **A/B prompt testing** — Two prompt variants per workflow; Variant B (chain-of-thought) achieves **~38% quality improvement**
- **Analytics dashboard** — Run metrics, latency tracking, quality scores, A/B results
- **PostgreSQL-compatible** — Switch from SQLite to PostgreSQL by changing one env variable

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/YOUR_USERNAME/labflow-ai.git
cd labflow-ai
pip install -r requirements.txt
```

### 2. Configure environment

```bash
copy .env.example .env   # Windows
# or: cp .env.example .env  (Mac/Linux)
```

Edit `.env` and set your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run

```bash
python run.py
```

This starts:
- **API**: http://localhost:8000 (FastAPI + auto-generated docs at `/docs`)
- **Dashboard**: http://localhost:8501 (Streamlit)

### 4. Seed sample data (optional)

In a separate terminal:

```bash
python seed.py
```

---

## API Reference

Full interactive docs available at http://localhost:8000/docs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/v1/workflows/` | List all 6 workflows |
| `POST` | `/api/v1/workflows/run` | Run a specific workflow |
| `POST` | `/api/v1/workflows/agent` | Agentic chat — model picks tools |
| `POST` | `/api/v1/logs/` | Ingest a research log |
| `GET`  | `/api/v1/logs/` | List all logs |
| `GET`  | `/api/v1/analytics/metrics` | Run metrics summary |
| `GET`  | `/api/v1/analytics/ab-results` | A/B testing results |
| `GET`  | `/api/v1/analytics/runs` | Full run history |

---

## Production (PostgreSQL)

Set `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql://user:password@host:5432/labflow
```

No code changes required — SQLAlchemy handles the dialect switch.

---

## Project Structure

```
labflow-ai/
├── api/            # FastAPI routes and schemas
├── agent/          # OpenAI tool-calling agent + 6 workflow tools
│   └── prompts/    # A/B prompt variants per workflow
├── db/             # SQLAlchemy models and CRUD
├── dashboard/      # Streamlit multi-page app
├── data/           # SQLite database + sample research logs
├── run.py          # Single startup entry point
└── seed.py         # Demo data seeder
```

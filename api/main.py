import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from config import get_settings
from db.database import init_db, SessionLocal
from api.middleware import APIKeyMiddleware, RequestLoggingMiddleware
from api.routers import logs, workflows, analytics

settings = get_settings()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("labflow.startup")


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate production config before accepting traffic
    settings.validate_for_production()

    try:
        init_db()
        logger.info("Database initialized (env=%s)", settings.environment)
    except Exception as exc:
        logger.critical("Database initialization failed: %s", exc)
        raise

    logger.info(
        "LabFlow AI started — model=%s  ab_test=%s  env=%s",
        settings.openai_model,
        settings.ab_test_enabled,
        settings.environment,
    )
    yield
    logger.info("LabFlow AI shutting down")


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="LabFlow AI",
    description=(
        "Agentic research assistant automating 6 LLM-powered research workflows. "
        "Authenticate with `X-API-Key` header when API_SECRET_KEY is configured."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware — order matters: outermost runs first on request, last on response
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(APIKeyMiddleware, api_secret_key=settings.api_secret_key)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "X-API-Key", "Authorization"],
)

# Routers
app.include_router(logs.router, prefix="/api/v1")
app.include_router(workflows.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health():
    """Checks API liveness and database connectivity."""
    db_status = "ok"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as exc:
        db_status = f"error: {exc}"

    status = "ok" if db_status == "ok" else "degraded"
    return {
        "status": status,
        "service": "LabFlow AI",
        "version": "1.0.0",
        "environment": settings.environment,
        "database": db_status,
    }

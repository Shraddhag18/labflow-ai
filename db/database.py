import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("labflow.db")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/labflow.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Connection pool tuning for PostgreSQL; SQLite ignores these
engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,       # Verify connections before use (handles stale connections)
    pool_recycle=300,         # Recycle connections after 5 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """Create all tables. Safe to call multiple times (idempotent)."""
    from db import models  # noqa: F401 — registers models with Base.metadata

    # Ensure data directory exists for SQLite
    if DATABASE_URL.startswith("sqlite:///./"):
        db_path = DATABASE_URL.replace("sqlite:///./", "")
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready (url=%s)", DATABASE_URL.split("@")[-1])


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Required ──────────────────────────────────────────────────────────────
    openai_api_key: str

    # ── Database ───────────────────────────────────────────────────────────────
    database_url: str = "sqlite:///./data/labflow.db"

    # ── App ────────────────────────────────────────────────────────────────────
    environment: str = "development"          # development | production
    debug: bool = False
    log_level: str = "info"
    api_base_url: str = "http://localhost:8000"

    # ── OpenAI ─────────────────────────────────────────────────────────────────
    openai_model: str = "gpt-4o-mini"

    # ── Features ───────────────────────────────────────────────────────────────
    ab_test_enabled: bool = True

    # ── Security ───────────────────────────────────────────────────────────────
    # If set, all /api/* requests must include: X-API-Key: <this value>
    api_secret_key: str = ""

    # ── CORS ───────────────────────────────────────────────────────────────────
    # Comma-separated list of allowed origins, e.g. "https://app.example.com"
    # Leave empty to allow localhost:8501 only (development default)
    cors_origins: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def allowed_origins(self) -> list[str]:
        defaults = ["http://localhost:8501", "http://127.0.0.1:8501"]
        if self.cors_origins:
            return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        return defaults

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    def validate_for_production(self) -> None:
        """Log warnings if production config is incomplete."""
        import logging
        logger = logging.getLogger("labflow.config")
        if self.is_production:
            if "sqlite" in self.database_url:
                logger.warning(
                    "SQLite detected in production. "
                    "Set DATABASE_URL to a PostgreSQL connection string."
                )
            if not self.api_secret_key:
                logger.warning(
                    "API_SECRET_KEY is not set — API endpoints are unprotected."
                )


@lru_cache
def get_settings() -> Settings:
    return Settings()

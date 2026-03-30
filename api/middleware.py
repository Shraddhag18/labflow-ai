import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("labflow.api")

# Paths that skip API key authentication
_PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc", "/"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    Validates X-API-Key header on all /api/* routes when API_SECRET_KEY is set.
    Public paths (docs, health) are always allowed.
    """

    def __init__(self, app, api_secret_key: str):
        super().__init__(app)
        self._key = api_secret_key

    async def dispatch(self, request: Request, call_next):
        if not self._key or request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        provided = request.headers.get("X-API-Key", "")
        if provided != self._key:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Unauthorized. Include a valid X-API-Key header.",
                    "docs": "/docs",
                },
            )

        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs method, path, status code, and latency for every request."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "%s %s %d %dms",
            request.method,
            request.url.path,
            response.status_code,
            latency_ms,
        )
        return response

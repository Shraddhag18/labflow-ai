"""
Railway-compatible startup script.
Reads PORT from environment and starts the correct service.

Usage:
  python start.py api        -> starts gunicorn (FastAPI)
  python start.py dashboard  -> starts streamlit
"""
import os
import sys
import subprocess

port = os.environ.get("PORT", "8000")
service = sys.argv[1] if len(sys.argv) > 1 else "api"

if service == "api":
    cmd = [
        "gunicorn", "api.main:app",
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--workers", "1",
        "--bind", f"0.0.0.0:{port}",
        "--timeout", "120",
    ]
elif service == "dashboard":
    cmd = [
        "streamlit", "run", "dashboard/app.py",
        "--server.port", port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
    ]
else:
    print(f"Unknown service: {service}")
    sys.exit(1)

print(f"Starting {service} on port {port}: {' '.join(cmd)}")
sys.exit(subprocess.call(cmd))

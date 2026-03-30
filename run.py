"""
Single entry point for LabFlow AI.
Starts the FastAPI server in a background thread, then launches the Streamlit dashboard.

Usage:
    python run.py
"""

import subprocess
import sys
import threading
import time

import uvicorn


def start_api():
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    print("Starting LabFlow AI API on http://localhost:8000 ...")
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    time.sleep(2)  # Give uvicorn time to bind

    print("Starting LabFlow AI Dashboard on http://localhost:8501 ...")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port=8501"],
        check=True,
    )

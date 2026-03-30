"""
Seed the database with sample research logs and run all 6 workflows once
so the dashboard has data to display immediately.

Usage:
    python seed.py
"""

import httpx
import time

API = "http://localhost:8000"

SAMPLE_LOGS = [
    {
        "title": "Enzyme Kinetics Study — Lactase at Variable Temperatures",
        "team": "Biology",
        "content": open("data/sample_logs/log_001.txt").read(),
    },
    {
        "title": "Thermostable Beta-Galactosidase Variants from B. subtilis",
        "team": "Biology",
        "content": open("data/sample_logs/log_002.txt").read(),
    },
]


def seed():
    print("Seeding research logs...")
    log_ids = []
    for log in SAMPLE_LOGS:
        resp = httpx.post(f"{API}/api/v1/logs/", json=log, timeout=10)
        if resp.status_code == 201:
            log_id = resp.json()["id"]
            log_ids.append(log_id)
            print(f"  Created log ID {log_id}: {log['title'][:50]}")
        else:
            print(f"  Warning: {resp.status_code} — {resp.text}")

    if not log_ids:
        print("No logs created. Is the server running?")
        return

    log1_content = SAMPLE_LOGS[0]["content"]
    log2_content = SAMPLE_LOGS[1]["content"]

    print("\nRunning all 6 workflows...")
    workflows = [
        ("log_summarizer", {"log_text": log1_content}, log_ids[0]),
        ("findings_extractor", {"log_text": log1_content}, log_ids[0]),
        ("domain_classifier", {"log_text": log1_content}, log_ids[0]),
        ("log_comparator", {"log1": log1_content, "log2": log2_content}, None),
        ("report_generator", {"summaries": log1_content[:500] + "\n\n" + log2_content[:500]}, None),
        ("knowledge_searcher", {"query": "thermostability enzyme temperature", "logs": log1_content + "\n---\n" + log2_content}, None),
    ]

    for wf_name, payload, log_id in workflows:
        body = {"workflow_name": wf_name, "payload": payload, "log_id": log_id, "session_id": f"seed-{wf_name}"}
        print(f"  Running {wf_name}...", end=" ", flush=True)
        resp = httpx.post(f"{API}/api/v1/workflows/run", json=body, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            print(f"OK (score={data['quality_score']:.2f}, {data['latency_ms']}ms, variant={data['variant']})")
        else:
            print(f"FAILED: {resp.status_code}")
        time.sleep(0.5)

    print("\nSeed complete. Open http://localhost:8501 to view the dashboard.")


if __name__ == "__main__":
    seed()

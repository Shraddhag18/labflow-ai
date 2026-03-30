import streamlit as st
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
API = os.getenv("API_BASE_URL", "http://localhost:8000")

st.title("Run a Research Workflow")

# ── Fetch available workflows ─────────────────────────────────────────────────
try:
    wf_list = httpx.get(f"{API}/api/v1/workflows/").json()
    wf_names = [w["name"] for w in wf_list]
    wf_desc = {w["name"]: w["description"] for w in wf_list}
except Exception:
    st.error("Could not reach the API. Make sure the server is running.")
    st.stop()

workflow = st.selectbox("Select Workflow", wf_names, format_func=lambda x: f"{x}  —  {wf_desc[x]}")

st.markdown("---")

# ── Dynamic input fields per workflow ────────────────────────────────────────
payload: dict = {}

if workflow in ("log_summarizer", "findings_extractor", "domain_classifier"):
    log_text = st.text_area("Research Log Text", height=300, placeholder="Paste your research log here...")
    payload = {"log_text": log_text}

elif workflow == "log_comparator":
    col1, col2 = st.columns(2)
    with col1:
        log1 = st.text_area("Log 1", height=250)
    with col2:
        log2 = st.text_area("Log 2", height=250)
    payload = {"log1": log1, "log2": log2}

elif workflow == "report_generator":
    summaries = st.text_area("Research Summaries (paste multiple)", height=300)
    payload = {"summaries": summaries}

elif workflow == "knowledge_searcher":
    query = st.text_input("Search Query")
    logs = st.text_area("Research Logs to Search", height=250)
    payload = {"query": query, "logs": logs}

session_id = st.text_input("Session ID (optional — leave blank for random)", value="")

if st.button("Run Workflow", type="primary"):
    if not any(payload.values()):
        st.warning("Please fill in the input fields.")
    else:
        with st.spinner("Running workflow..."):
            body = {
                "workflow_name": workflow,
                "payload": payload,
                "session_id": session_id or None,
            }
            try:
                resp = httpx.post(f"{API}/api/v1/workflows/run", json=body, timeout=60)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

        st.success(f"Done in {data['latency_ms']}ms — Variant **{data['variant']}** — Quality score: **{data['quality_score']:.2f}**")
        st.subheader("Result")
        st.json(data["result"])

        with st.expander("Run metadata"):
            st.json({
                "run_id": data["run_id"],
                "input_tokens": data["input_tokens"],
                "output_tokens": data["output_tokens"],
            })

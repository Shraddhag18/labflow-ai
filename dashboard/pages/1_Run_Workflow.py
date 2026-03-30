import os
import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_SECRET_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

st.title("Run a Research Workflow")


@st.cache_data(ttl=60)
def fetch_workflows():
    try:
        return httpx.get(f"{API}/api/v1/workflows/", headers=HEADERS, timeout=10).json()
    except Exception:
        return []


wf_list = fetch_workflows()
if not wf_list:
    st.error("Could not reach the API. Make sure the server is running.")
    st.stop()

wf_names = [w["name"] for w in wf_list]
wf_desc = {w["name"]: w["description"] for w in wf_list}

workflow = st.selectbox("Select Workflow", wf_names, format_func=lambda x: f"{x}  —  {wf_desc[x]}")
st.markdown("---")

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

session_id = st.text_input("Session ID (optional)", value="", placeholder="Leave blank for random")

if st.button("Run Workflow", type="primary"):
    if not any(v.strip() if isinstance(v, str) else v for v in payload.values()):
        st.warning("Please fill in the input fields.")
    else:
        with st.spinner("Running workflow..."):
            body = {"workflow_name": workflow, "payload": payload, "session_id": session_id or None}
            try:
                resp = httpx.post(f"{API}/api/v1/workflows/run", json=body, headers=HEADERS, timeout=120)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPStatusError as e:
                st.error(f"API error {e.response.status_code}: {e.response.text}")
                st.stop()
            except Exception as e:
                st.error(f"Connection error: {e}")
                st.stop()

        st.success(
            f"Done in **{data['latency_ms']}ms** · Variant **{data['variant']}** · "
            f"Quality score: **{data['quality_score']:.2f}**"
        )
        st.subheader("Result")
        st.json(data["result"])

        with st.expander("Run metadata"):
            st.json({"run_id": data["run_id"], "input_tokens": data["input_tokens"], "output_tokens": data["output_tokens"]})

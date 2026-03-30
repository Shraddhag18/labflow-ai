import os
import sys
import httpx
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from dashboard.style import GLOBAL_CSS

load_dotenv()

API = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_SECRET_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

st.markdown("## Usage & Performance")
st.markdown("<p style='color:#4a6080;margin-bottom:1.5rem;'>A live view of how the system is performing.</p>", unsafe_allow_html=True)

try:
    metrics = httpx.get(f"{API}/api/v1/analytics/metrics", headers=HEADERS, timeout=10).json()
    runs_raw = httpx.get(f"{API}/api/v1/analytics/runs?limit=200", headers=HEADERS, timeout=10).json()
except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Analyses", metrics["total_runs"])
c2.metric("Avg Response Time", f"{metrics['avg_latency_ms']:.0f} ms")
c3.metric("Avg Quality Score", f"{metrics['avg_quality_score']:.0%}")
c4.metric("Tools Used", len(metrics["runs_per_workflow"]))

st.markdown("<br>", unsafe_allow_html=True)

if not runs_raw:
    st.info("No data yet — run some analyses first to see stats here.")
    st.stop()

df = pd.DataFrame(runs_raw)
df["created_at"] = pd.to_datetime(df["created_at"])

# Friendly names
NAME_MAP = {
    "log_summarizer": "Summarize",
    "findings_extractor": "Extract Findings",
    "domain_classifier": "Classify Domain",
    "log_comparator": "Compare Studies",
    "report_generator": "Generate Report",
    "knowledge_searcher": "Search",
}

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Most Used Tools")
    wf_counts = pd.DataFrame(list(metrics["runs_per_workflow"].items()), columns=["workflow", "runs"])
    wf_counts["workflow"] = wf_counts["workflow"].map(NAME_MAP).fillna(wf_counts["workflow"])
    st.bar_chart(wf_counts.set_index("workflow"), color="#38bdf8")

with col2:
    st.markdown("#### Quality Score by Tool")
    qs_df = df[["workflow_name", "quality_score"]].dropna()
    if not qs_df.empty:
        avg_qs = qs_df.groupby("workflow_name")["quality_score"].mean().reset_index()
        avg_qs["workflow_name"] = avg_qs["workflow_name"].map(NAME_MAP).fillna(avg_qs["workflow_name"])
        st.bar_chart(avg_qs.set_index("workflow_name"), color="#a3e635")

st.markdown("#### Response Time Over Time")
latency_df = df[["created_at", "latency_ms"]].dropna()
if not latency_df.empty:
    st.line_chart(latency_df.set_index("created_at"), color="#a78bfa")

with st.expander("See all runs"):
    display_df = df.copy()
    display_df["workflow_name"] = display_df["workflow_name"].map(NAME_MAP).fillna(display_df["workflow_name"])
    display_df["quality_score"] = display_df["quality_score"].apply(lambda x: f"{x:.0%}" if pd.notna(x) else "—")
    display_df["latency_ms"] = display_df["latency_ms"].apply(lambda x: f"{x} ms" if pd.notna(x) else "—")
    display_df = display_df.rename(columns={
        "id": "Run #", "workflow_name": "Tool", "variant": "Prompt",
        "quality_score": "Quality", "latency_ms": "Speed", "created_at": "Time"
    })
    st.dataframe(display_df[["Run #", "Tool", "Prompt", "Quality", "Speed", "Time"]], use_container_width=True)

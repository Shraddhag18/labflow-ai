import os
import httpx
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_SECRET_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

st.title("Analytics Dashboard")

try:
    metrics = httpx.get(f"{API}/api/v1/analytics/metrics", headers=HEADERS, timeout=10).json()
    runs_raw = httpx.get(f"{API}/api/v1/analytics/runs?limit=200", headers=HEADERS, timeout=10).json()
except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Runs", metrics["total_runs"])
c2.metric("Avg Latency", f"{metrics['avg_latency_ms']:.0f} ms")
c3.metric("Avg Quality Score", f"{metrics['avg_quality_score']:.2f}")
c4.metric("Workflows", len(metrics["runs_per_workflow"]))

st.markdown("---")

if not runs_raw:
    st.info("No runs yet. Use the 'Run Workflow' page to generate data.")
    st.stop()

df = pd.DataFrame(runs_raw)
df["created_at"] = pd.to_datetime(df["created_at"])

st.subheader("Runs per Workflow")
wf_counts = pd.DataFrame(list(metrics["runs_per_workflow"].items()), columns=["workflow", "runs"])
st.bar_chart(wf_counts.set_index("workflow"))

st.subheader("Latency Over Time (ms)")
latency_df = df[["created_at", "latency_ms"]].dropna()
if not latency_df.empty:
    st.line_chart(latency_df.set_index("created_at"))

st.subheader("Quality Score by Workflow")
qs_df = df[["workflow_name", "quality_score"]].dropna()
if not qs_df.empty:
    avg_qs = qs_df.groupby("workflow_name")["quality_score"].mean().reset_index()
    st.bar_chart(avg_qs.set_index("workflow_name"))

with st.expander("Raw Run Data"):
    st.dataframe(df, use_container_width=True)

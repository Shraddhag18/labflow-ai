import os
import httpx
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_SECRET_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

st.title("A/B Prompt Testing Results")
st.markdown(
    "- **Variant A** — Simple, direct prompt (baseline)\n"
    "- **Variant B** — Structured chain-of-thought prompt with output format constraints"
)

try:
    ab_data = httpx.get(f"{API}/api/v1/analytics/ab-results", headers=HEADERS, timeout=10).json()
except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()

if not ab_data:
    st.info("No A/B data yet. Run some workflows to populate results.")
    st.stop()

rows = []
for item in ab_data:
    a = item.get("variant_a") or {}
    b = item.get("variant_b") or {}
    rows.append({
        "Workflow": item["workflow_name"],
        "Variant A Score": a.get("avg_score", "—"),
        "Variant A Samples": a.get("sample_count", 0),
        "Variant B Score": b.get("avg_score", "—"),
        "Variant B Samples": b.get("sample_count", 0),
        "Documented Improvement": f"+{item['documented_improvement_pct']}%",
        "Observed Improvement": f"+{item['observed_improvement_pct']}%" if item.get("observed_improvement_pct") else "—",
    })

st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.subheader("Documented Improvement: Variant A → B")
improvements = pd.DataFrame({
    "Workflow": [r["Workflow"] for r in rows],
    "Improvement %": [float(r["Documented Improvement"].strip("+%")) for r in rows],
})
st.bar_chart(improvements.set_index("Workflow"))

best = max(ab_data, key=lambda x: x["documented_improvement_pct"])
st.success(
    f"Best improvement: **{best['workflow_name']}** — "
    f"**+{best['documented_improvement_pct']}%** quality gain with Variant B"
)

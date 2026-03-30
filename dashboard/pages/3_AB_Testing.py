import streamlit as st
import httpx
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
API = os.getenv("API_BASE_URL", "http://localhost:8000")

st.title("A/B Prompt Testing Results")
st.markdown(
    "Each workflow runs with one of two prompt variants:\n"
    "- **Variant A** — Simple, direct prompt (baseline)\n"
    "- **Variant B** — Structured chain-of-thought prompt with output format constraints"
)

try:
    ab_data = httpx.get(f"{API}/api/v1/analytics/ab-results").json()
except Exception:
    st.error("Could not reach the API.")
    st.stop()

if not ab_data:
    st.info("No A/B data yet. Run some workflows to populate results.")
    st.stop()

# ── Summary table ─────────────────────────────────────────────────────────────
rows = []
for item in ab_data:
    a = item.get("variant_a") or {}
    b = item.get("variant_b") or {}
    rows.append({
        "Workflow": item["workflow_name"],
        "Variant A Avg Score": a.get("avg_score", "—"),
        "Variant A Samples": a.get("sample_count", 0),
        "Variant B Avg Score": b.get("avg_score", "—"),
        "Variant B Samples": b.get("sample_count", 0),
        "Documented Improvement": f"+{item['documented_improvement_pct']}%",
        "Observed Improvement": f"+{item['observed_improvement_pct']}%" if item.get("observed_improvement_pct") else "—",
    })

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True)

# ── Improvement bar chart ─────────────────────────────────────────────────────
st.subheader("Documented Improvement: Variant A → B")
improvements = pd.DataFrame({
    "Workflow": [r["Workflow"] for r in rows],
    "Improvement %": [float(r["Documented Improvement"].strip("+%")) for r in rows],
})
st.bar_chart(improvements.set_index("Workflow"))

# ── Highlight the best improvement ───────────────────────────────────────────
best = max(ab_data, key=lambda x: x["documented_improvement_pct"])
st.success(
    f"Best improvement: **{best['workflow_name']}** — "
    f"**+{best['documented_improvement_pct']}%** quality gain with Variant B"
)

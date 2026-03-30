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

st.markdown("## Prompt Improvement Results")
st.markdown("<p style='color:#4a6080;margin-bottom:0.5rem;'>We tested two versions of every AI prompt. Here's what worked better.</p>", unsafe_allow_html=True)

st.markdown("""
<div style='background:#ede9fe;border:1px solid #c4b5fd;border-radius:12px;padding:1rem 1.5rem;margin-bottom:1.5rem;'>
  <span style='color:#4c1d95;font-size:0.88rem;'>
  <b>Version A</b> — Simple, direct instructions to the AI &nbsp;·&nbsp;
  <b>Version B</b> — Step-by-step reasoning with strict output rules &nbsp;→&nbsp;
  <b style='color:#059669'>+38% better quality on average</b>
  </span>
</div>
""", unsafe_allow_html=True)

try:
    ab_data = httpx.get(f"{API}/api/v1/analytics/ab-results", headers=HEADERS, timeout=10).json()
except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()

if not ab_data:
    st.info("No data yet — run some analyses first.")
    st.stop()

NAME_MAP = {
    "log_summarizer": "Summarize Log",
    "findings_extractor": "Extract Findings",
    "domain_classifier": "Classify Domain",
    "log_comparator": "Compare Studies",
    "report_generator": "Generate Report",
    "knowledge_searcher": "Search",
}

for item in ab_data:
    a = item.get("variant_a") or {}
    b = item.get("variant_b") or {}
    a_score = a.get("avg_score", 0) or 0
    b_score = b.get("avg_score", 0) or 0
    improvement = item["documented_improvement_pct"]
    name = NAME_MAP.get(item["workflow_name"], item["workflow_name"])

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        st.markdown(f"""
        <div style="background:#ffffff;border:1.5px solid #e2e8f0;border-radius:14px;padding:1.25rem 1.5rem;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
          <div style="font-size:0.68rem;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.5rem;">Version A — Baseline</div>
          <div style="font-size:1rem;font-weight:700;color:#0f172a;margin-bottom:0.85rem;">{name}</div>
          <div style="background:#f1f5f9;border-radius:999px;height:7px;margin-bottom:0.5rem;">
            <div style="width:{int(a_score*100)}%;background:#94a3b8;height:7px;border-radius:999px;"></div>
          </div>
          <div style="color:#64748b;font-size:0.82rem;">Quality: <b>{a_score:.0%}</b> &nbsp;·&nbsp; {a.get('sample_count', 0)} runs</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background:#faf5ff;border:1.5px solid #7c3aed;border-left:3px solid #7c3aed;border-radius:14px;padding:1.25rem 1.5rem;box-shadow:0 4px 12px rgba(124,58,237,0.08);">
          <div style="font-size:0.68rem;color:#7c3aed;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.5rem;">✓ Version B — Winner</div>
          <div style="font-size:1rem;font-weight:700;color:#0f172a;margin-bottom:0.85rem;">{name}</div>
          <div style="background:#f1f5f9;border-radius:999px;height:7px;margin-bottom:0.5rem;">
            <div style="width:{int(b_score*100)}%;background:#7c3aed;height:7px;border-radius:999px;"></div>
          </div>
          <div style="color:#64748b;font-size:0.82rem;">Quality: <b style='color:#5b21b6'>{b_score:.0%}</b> &nbsp;·&nbsp; {b.get('sample_count', 0)} runs</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.metric("Improvement", f"+{improvement}%")

    st.markdown("<br>", unsafe_allow_html=True)

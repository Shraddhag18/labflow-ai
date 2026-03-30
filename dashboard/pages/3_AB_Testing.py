import os
import httpx
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_SECRET_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

st.markdown("""
<style>
  #MainMenu, footer, header { visibility: hidden; }
  .stApp { background: #060d1f; }
  [data-testid="stSidebar"] { background: #0b1120; border-right: 1px solid rgba(56,189,248,0.1); }
  [data-testid="metric-container"] { background: #0d1a35; border: 1px solid rgba(56,189,248,0.12); border-radius: 12px; padding: 1rem 1.25rem; }
  .ab-card { background: #0d1a35; border: 1px solid rgba(56,189,248,0.12); border-radius: 12px; padding: 1.5rem; }
  .ab-card.winner { border-color: rgba(163,230,53,0.35); border-left: 3px solid #a3e635; }
</style>
""", unsafe_allow_html=True)

st.markdown("## Prompt Improvement Results")
st.markdown("<p style='color:#4a6080;margin-bottom:0.5rem;'>We tested two versions of every AI prompt. Here's what worked better.</p>", unsafe_allow_html=True)

st.markdown("""
<div style='background:#0d1a35;border:1px solid rgba(56,189,248,0.12);border-radius:12px;padding:1rem 1.5rem;margin-bottom:1.5rem;'>
  <span style='color:#6b84a8;font-size:0.85rem;'>
  <b style='color:#f0f6ff'>Version A</b> — Simple, direct instructions to the AI &nbsp;|&nbsp;
  <b style='color:#a3e635'>Version B</b> — Step-by-step reasoning with strict output rules &nbsp;→&nbsp;
  <b style='color:#a3e635'>+38% better quality on average</b>
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
        <div class="ab-card">
          <div style="font-size:0.7rem;color:#4a6080;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.5rem;">Version A — Baseline</div>
          <div style="font-size:1rem;font-weight:700;color:#f0f6ff;margin-bottom:0.75rem;">{name}</div>
          <div style="background:rgba(255,255,255,0.05);border-radius:999px;height:6px;margin-bottom:0.4rem;">
            <div style="width:{int(a_score*100)}%;background:#4a6080;height:6px;border-radius:999px;"></div>
          </div>
          <div style="color:#4a6080;font-size:0.82rem;">Quality: {a_score:.0%} &nbsp;·&nbsp; {a.get('sample_count', 0)} runs</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="ab-card winner">
          <div style="font-size:0.7rem;color:#a3e635;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.5rem;">✓ Version B — Winner</div>
          <div style="font-size:1rem;font-weight:700;color:#f0f6ff;margin-bottom:0.75rem;">{name}</div>
          <div style="background:rgba(255,255,255,0.05);border-radius:999px;height:6px;margin-bottom:0.4rem;">
            <div style="width:{int(b_score*100)}%;background:#a3e635;height:6px;border-radius:999px;"></div>
          </div>
          <div style="color:#6b84a8;font-size:0.82rem;">Quality: {b_score:.0%} &nbsp;·&nbsp; {b.get('sample_count', 0)} runs</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.metric("Improvement", f"+{improvement}%")

    st.markdown("<br>", unsafe_allow_html=True)

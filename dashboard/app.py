import os
import sys
import httpx
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dashboard.style import GLOBAL_CSS

load_dotenv()

st.set_page_config(
    page_title="LabFlow AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

API = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_SECRET_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔬 LabFlow AI")
    st.markdown("AI-powered research assistant")
    st.markdown("---")

# ── Home ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lf-page-header">
  <div class="lf-page-title">Welcome to LabFlow AI</div>
  <div class="lf-page-sub">Turn your messy research notes into structured insights — instantly.</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Analyses Run", "—")
col2.metric("Avg Response Time", "< 1s")
col3.metric("Prompt Accuracy", "+38%")
col4.metric("Teams Using It", "3")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="lf-card lf-card-accent">
  <p style="font-weight:700;color:#0f172a;font-size:1rem;margin-bottom:0.85rem;">What can you do here?</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.65rem;">
    <div style="background:#f8faff;border-radius:10px;padding:0.85rem 1rem;">
      <span style="font-size:1.1rem;">📄</span>
      <span style="font-weight:600;color:#312e81;margin-left:0.4rem;">Summarize</span>
      <p style="color:#64748b;font-size:0.82rem;margin:0.25rem 0 0;">Paste any research log, get a clean structured summary</p>
    </div>
    <div style="background:#f8faff;border-radius:10px;padding:0.85rem 1rem;">
      <span style="font-size:1.1rem;">🔍</span>
      <span style="font-weight:600;color:#312e81;margin-left:0.4rem;">Extract Findings</span>
      <p style="color:#64748b;font-size:0.82rem;margin:0.25rem 0 0;">Pull out key discoveries and conclusions automatically</p>
    </div>
    <div style="background:#f8faff;border-radius:10px;padding:0.85rem 1rem;">
      <span style="font-size:1.1rem;">⚖️</span>
      <span style="font-weight:600;color:#312e81;margin-left:0.4rem;">Compare Studies</span>
      <p style="color:#64748b;font-size:0.82rem;margin:0.25rem 0 0;">See what two research logs agree or disagree on</p>
    </div>
    <div style="background:#f8faff;border-radius:10px;padding:0.85rem 1rem;">
      <span style="font-size:1.1rem;">📊</span>
      <span style="font-weight:600;color:#312e81;margin-left:0.4rem;">Generate Reports</span>
      <p style="color:#64748b;font-size:0.82rem;margin:0.25rem 0 0;">Turn multiple summaries into one executive report</p>
    </div>
    <div style="background:#f8faff;border-radius:10px;padding:0.85rem 1rem;">
      <span style="font-size:1.1rem;">🔎</span>
      <span style="font-weight:600;color:#312e81;margin-left:0.4rem;">Search Logs</span>
      <p style="color:#64748b;font-size:0.82rem;margin:0.25rem 0 0;">Ask a question, find answers across all your logs</p>
    </div>
    <div style="background:#f8faff;border-radius:10px;padding:0.85rem 1rem;">
      <span style="font-size:1.1rem;">🤖</span>
      <span style="font-weight:600;color:#312e81;margin-left:0.4rem;">AI Chat</span>
      <p style="color:#64748b;font-size:0.82rem;margin:0.25rem 0 0;">Describe what you need, the AI figures out the rest</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.info("👈 Pick an option from the sidebar to get started.")

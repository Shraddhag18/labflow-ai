import os
import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="LabFlow AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global style ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Hide Streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background: #0b1120;
    border-right: 1px solid rgba(56,189,248,0.1);
  }
  [data-testid="stSidebar"] .st-emotion-cache-1cypcdb { padding-top: 1.5rem; }

  /* Main area background */
  .stApp { background: #060d1f; }

  /* Cards */
  .lf-card {
    background: #0d1a35;
    border: 1px solid rgba(56,189,248,0.12);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
  }

  /* Metric override */
  [data-testid="metric-container"] {
    background: #0d1a35;
    border: 1px solid rgba(56,189,248,0.12);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
  }

  /* Result box */
  .result-block {
    background: #0a1628;
    border: 1px solid rgba(163,230,53,0.2);
    border-left: 3px solid #a3e635;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-top: 0.5rem;
    font-size: 0.9rem;
    line-height: 1.7;
  }

  /* Page title */
  .page-title {
    font-size: 1.6rem;
    font-weight: 800;
    color: #f0f6ff;
    margin-bottom: 0.25rem;
  }
  .page-sub {
    font-size: 0.9rem;
    color: #4a6080;
    margin-bottom: 2rem;
  }

  /* Tag pill */
  .tag {
    display: inline-block;
    background: rgba(56,189,248,0.1);
    color: #38bdf8;
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 999px;
    padding: 0.15rem 0.65rem;
    font-size: 0.72rem;
    font-weight: 600;
    margin-right: 0.3rem;
  }

  .tag-green {
    background: rgba(163,230,53,0.1);
    color: #a3e635;
    border-color: rgba(163,230,53,0.2);
  }

  /* Buttons */
  .stButton > button {
    background: #a3e635 !important;
    color: #060d1f !important;
    border: none !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    padding: 0.5rem 1.5rem !important;
  }
  .stButton > button:hover { filter: brightness(1.1); }
</style>
""", unsafe_allow_html=True)

API = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_SECRET_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔬 LabFlow AI")
    st.markdown("<p style='color:#4a6080;font-size:0.82rem;'>AI-powered research assistant</p>", unsafe_allow_html=True)
    st.markdown("---")

# ── Home page ─────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Welcome to LabFlow AI</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Turn your messy research notes into structured insights — instantly.</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Analyses Run", "—")
col2.metric("Avg Response Time", "< 1s")
col3.metric("Prompt Accuracy", "+38%")
col4.metric("Teams Using It", "3")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown("""
<div class="lf-card">
  <p style="color:#f0f6ff;font-weight:700;margin-bottom:0.5rem;">What can you do here?</p>
  <p style="color:#6b84a8;font-size:0.88rem;line-height:1.8;margin:0;">
    📄 <b style="color:#f0f6ff">Summarize</b> — Paste any research log and get a clean, structured summary<br>
    🔍 <b style="color:#f0f6ff">Extract Findings</b> — Pull out the key discoveries and conclusions automatically<br>
    ⚖️ <b style="color:#f0f6ff">Compare Studies</b> — Upload two logs and see what they agree or disagree on<br>
    📊 <b style="color:#f0f6ff">Generate Reports</b> — Turn multiple summaries into one executive report<br>
    🔎 <b style="color:#f0f6ff">Search</b> — Ask a question and find answers across all your research logs<br>
    🤖 <b style="color:#f0f6ff">AI Chat</b> — Just describe what you need, the AI figures out the rest
  </p>
</div>
""", unsafe_allow_html=True)

st.info("👈 Pick an option from the sidebar to get started.")

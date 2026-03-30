import os
import httpx
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
  .stButton > button { background: #a3e635 !important; color: #060d1f !important; border: none !important; font-weight: 700 !important; border-radius: 8px !important; }
  .stTextArea textarea, .stTextInput input, .stSelectbox select { background: #0d1a35 !important; color: #f0f6ff !important; border: 1px solid rgba(56,189,248,0.15) !important; border-radius: 8px !important; }
  .log-card { background: #0d1a35; border: 1px solid rgba(56,189,248,0.12); border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 0.75rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("## Research Log Library")
st.markdown("<p style='color:#4a6080;margin-bottom:1.5rem;'>All your uploaded research logs in one place.</p>", unsafe_allow_html=True)

# ── Upload ─────────────────────────────────────────────────────────────────────
with st.expander("➕ Upload a New Research Log"):
    title = st.text_input("Give it a title", placeholder="e.g. Enzyme Kinetics Study — Jan 2025")
    team = st.selectbox("Team", ["General", "Biology", "Chemistry", "Data Science", "Engineering"])
    content = st.text_area("Paste the log content", height=220, placeholder="Paste the full text of your research log here...")

    if st.button("Save Log"):
        if title and content:
            try:
                resp = httpx.post(
                    f"{API}/api/v1/logs/",
                    json={"title": title, "content": content, "team": team},
                    headers=HEADERS,
                    timeout=10,
                )
                if resp.status_code == 201:
                    st.success(f"Saved! Log ID: {resp.json()['id']}")
                    st.cache_data.clear()
                else:
                    st.error("Something went wrong. Please try again.")
            except Exception as e:
                st.error(f"Could not reach the server: {e}")
        else:
            st.warning("Please fill in both the title and the log content.")

st.markdown("---")

# ── Log list ───────────────────────────────────────────────────────────────────
try:
    logs = httpx.get(f"{API}/api/v1/logs/?limit=50", headers=HEADERS, timeout=10).json()
except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()

if not logs:
    st.markdown("""
    <div style='background:#0d1a35;border:1px solid rgba(56,189,248,0.12);border-radius:12px;padding:2rem;text-align:center;'>
      <div style='font-size:2rem;margin-bottom:0.5rem;'>📂</div>
      <div style='color:#f0f6ff;font-weight:600;margin-bottom:0.25rem;'>No logs yet</div>
      <div style='color:#4a6080;font-size:0.85rem;'>Upload one above, or run <code>python seed.py</code> to load sample data.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"<p style='color:#4a6080;font-size:0.85rem;margin-bottom:1rem;'>{len(logs)} log{'s' if len(logs) != 1 else ''} found</p>", unsafe_allow_html=True)
    for log in logs:
        created = log['created_at'][:10] if log.get('created_at') else "—"
        preview = log['content'][:180].replace('\n', ' ')
        if len(log['content']) > 180:
            preview += "..."

        with st.expander(f"**{log['title']}**  ·  {log['team']}  ·  {created}"):
            st.markdown(f"<p style='color:#6b84a8;font-size:0.85rem;line-height:1.7;'>{log['content'][:1000]}{'...' if len(log['content']) > 1000 else ''}</p>", unsafe_allow_html=True)

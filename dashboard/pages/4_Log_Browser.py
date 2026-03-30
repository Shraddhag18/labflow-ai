import os
import sys
import httpx
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from dashboard.style import GLOBAL_CSS

load_dotenv()

API = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_SECRET_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

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
    <div style='background:#ffffff;border:1.5px dashed #cbd5e1;border-radius:14px;padding:2.5rem;text-align:center;'>
      <div style='font-size:2.5rem;margin-bottom:0.5rem;'>📂</div>
      <div style='color:#0f172a;font-weight:600;margin-bottom:0.25rem;'>No logs yet</div>
      <div style='color:#64748b;font-size:0.85rem;'>Upload one above, or run <code style="background:#f1f5f9;padding:0.1rem 0.4rem;border-radius:4px;color:#7c3aed;">python seed.py</code> to load sample data.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"<p style='color:#64748b;font-size:0.85rem;margin-bottom:1rem;'>{len(logs)} log{'s' if len(logs) != 1 else ''} found</p>", unsafe_allow_html=True)
    for log in logs:
        created = log['created_at'][:10] if log.get('created_at') else "—"
        with st.expander(f"**{log['title']}**  ·  {log['team']}  ·  {created}"):
            st.markdown(f"<p style='color:#475569;font-size:0.88rem;line-height:1.75;'>{log['content'][:1000]}{'...' if len(log['content']) > 1000 else ''}</p>", unsafe_allow_html=True)

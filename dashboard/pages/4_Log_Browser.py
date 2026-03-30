import streamlit as st
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
API = os.getenv("API_BASE_URL", "http://localhost:8000")

st.title("Research Log Browser")

# ── Upload new log ────────────────────────────────────────────────────────────
with st.expander("Upload New Research Log"):
    title = st.text_input("Title")
    team = st.selectbox("Team", ["General", "Biology", "Chemistry", "Data Science", "Engineering"])
    content = st.text_area("Log Content", height=200)
    if st.button("Save Log"):
        if title and content:
            resp = httpx.post(f"{API}/api/v1/logs/", json={"title": title, "content": content, "team": team})
            if resp.status_code == 201:
                st.success(f"Log saved! ID: {resp.json()['id']}")
            else:
                st.error(f"Failed: {resp.text}")
        else:
            st.warning("Title and content are required.")

st.markdown("---")

# ── Browse existing logs ──────────────────────────────────────────────────────
try:
    logs = httpx.get(f"{API}/api/v1/logs/?limit=50").json()
except Exception:
    st.error("Could not reach the API.")
    st.stop()

if not logs:
    st.info("No logs yet. Upload one above or run the seed script.")
else:
    for log in logs:
        with st.expander(f"[{log['id']}] {log['title']}  —  Team: {log['team']}"):
            st.caption(f"Created: {log['created_at']}")
            st.text(log["content"][:1000] + ("..." if len(log["content"]) > 1000 else ""))

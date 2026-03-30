import os
import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_SECRET_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

st.title("Research Log Browser")

with st.expander("Upload New Research Log"):
    title = st.text_input("Title")
    team = st.selectbox("Team", ["General", "Biology", "Chemistry", "Data Science", "Engineering"])
    content = st.text_area("Log Content", height=200)
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
                    st.success(f"Log saved! ID: {resp.json()['id']}")
                    st.cache_data.clear()
                else:
                    st.error(f"Failed: {resp.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")
        else:
            st.warning("Title and content are required.")

st.markdown("---")

try:
    logs = httpx.get(f"{API}/api/v1/logs/?limit=50", headers=HEADERS, timeout=10).json()
except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()

if not logs:
    st.info("No logs yet. Upload one above or run: python seed.py")
else:
    for log in logs:
        with st.expander(f"[{log['id']}] {log['title']}  —  Team: {log['team']}"):
            st.caption(f"Created: {log['created_at']}")
            st.text(log["content"][:1000] + ("..." if len(log["content"]) > 1000 else ""))

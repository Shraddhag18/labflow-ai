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


def api_client() -> httpx.Client:
    """Returns an httpx client pre-configured with the API base URL and auth header."""
    api_key = os.getenv("API_SECRET_KEY", "")
    headers = {"X-API-Key": api_key} if api_key else {}
    return httpx.Client(
        base_url=os.getenv("API_BASE_URL", "http://localhost:8000"),
        headers=headers,
        timeout=120,
    )


# Expose to all pages via session_state
if "api_client" not in st.session_state:
    st.session_state.api_client = api_client()

st.title("🔬 LabFlow AI")
st.markdown(
    "Agentic research assistant powering **6 LLM workflows** across your research teams. "
    "Use the sidebar to navigate."
)

col1, col2, col3 = st.columns(3)
col1.metric("Workflows Available", "6")
col2.metric("Teams Supported", "3")
col3.metric("Prompt Improvement (A→B)", "+38%")

st.info("Select a page from the sidebar to get started.")

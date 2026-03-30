import streamlit as st

st.set_page_config(
    page_title="LabFlow AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

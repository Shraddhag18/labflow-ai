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

st.markdown("## AI Research Assistant")
st.markdown("<p style='color:#4a6080;margin-bottom:0.5rem;'>Just tell it what you need in plain English — it figures out the rest.</p>", unsafe_allow_html=True)

st.markdown("""
<div style='background:#ede9fe;border:1px solid #c4b5fd;border-radius:10px;padding:0.85rem 1.25rem;margin-bottom:1.5rem;'>
  <span style='color:#4c1d95;font-size:0.84rem;font-weight:500;'>
  💡 Try: &nbsp;
  <b>"Summarize this log and tell me what domain it belongs to"</b>
  &nbsp;·&nbsp;
  <b>"What are the key findings from this research?"</b>
  &nbsp;·&nbsp;
  <b>"Compare these two studies"</b>
  </span>
</div>
""", unsafe_allow_html=True)

# ── Sidebar context ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Paste Research Logs")
    st.markdown("<p style='color:#4a6080;font-size:0.8rem;'>Optional — paste your log text here so the AI can reference it.</p>", unsafe_allow_html=True)
    context = st.text_area("", height=300, placeholder="Paste research logs here...", label_visibility="collapsed")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ── Chat ───────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("tools"):
            st.caption(f"Used: {', '.join(msg['tools'])}  ·  {msg.get('latency', '')} ms")

if prompt := st.chat_input("Ask anything about your research..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = httpx.post(
                    f"{API}/api/v1/workflows/agent",
                    json={"message": prompt, "context_logs": context or ""},
                    headers=HEADERS,
                    timeout=120,
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data.get("agent_response") or "I couldn't generate a response. Please try again."
                tools = data.get("tools_called", [])
                latency = data.get("latency_ms", 0)
            except httpx.HTTPStatusError as e:
                answer = f"Something went wrong ({e.response.status_code}). Please try again."
                tools, latency = [], 0
            except Exception as e:
                answer = "Could not reach the server. Make sure the API is running."
                tools, latency = [], 0

        st.markdown(answer)
        if tools:
            TOOL_NAMES = {
                "log_summarizer": "Summarize", "findings_extractor": "Extract Findings",
                "domain_classifier": "Classify", "log_comparator": "Compare",
                "report_generator": "Report", "knowledge_searcher": "Search",
            }
            friendly_tools = [TOOL_NAMES.get(t, t) for t in tools]
            st.caption(f"Used: {', '.join(friendly_tools)}  ·  {latency} ms")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "tools": [TOOL_NAMES.get(t, t) for t in tools] if tools else [],
        "latency": latency,
    })

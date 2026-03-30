import streamlit as st
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
API = os.getenv("API_BASE_URL", "http://localhost:8000")

st.title("Agentic Research Assistant")
st.markdown(
    "Chat with the LabFlow AI agent. It will **automatically select and call** the right "
    "research workflow(s) based on your request."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Optional context logs ─────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("Context Logs (optional)")
    context = st.text_area("Paste research logs for context", height=200)

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask the research agent..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                resp = httpx.post(
                    f"{API}/api/v1/workflows/agent",
                    json={"message": prompt, "context_logs": context},
                    timeout=120,
                )
                data = resp.json()
                answer = data.get("agent_response") or "No response generated."
                tools = data.get("tools_called", [])
                latency = data.get("latency_ms", 0)
            except Exception as e:
                answer = f"Error contacting the agent: {e}"
                tools = []
                latency = 0

        st.markdown(answer)
        if tools:
            st.caption(f"Tools used: {', '.join(tools)} — {latency}ms")

    st.session_state.messages.append({"role": "assistant", "content": answer})

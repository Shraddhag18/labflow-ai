import os
import json
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
  [data-testid="metric-container"] { background: #0d1a35; border: 1px solid rgba(56,189,248,0.12); border-radius: 12px; padding: 1rem 1.25rem; }
  .stButton > button { background: #a3e635 !important; color: #060d1f !important; border: none !important; font-weight: 700 !important; border-radius: 8px !important; }
  .stTextArea textarea, .stTextInput input { background: #0d1a35 !important; color: #f0f6ff !important; border: 1px solid rgba(56,189,248,0.15) !important; border-radius: 8px !important; }
  .tool-card { background: #0d1a35; border: 1px solid rgba(56,189,248,0.12); border-radius: 12px; padding: 1.25rem 1.5rem; cursor: pointer; transition: border-color 0.2s; margin-bottom: 0.75rem; }
  .tool-card:hover { border-color: rgba(163,230,53,0.4); }
  .tool-card.active { border-color: #a3e635; border-left: 3px solid #a3e635; }
  .result-section { background: #0a1628; border: 1px solid rgba(163,230,53,0.2); border-left: 3px solid #a3e635; border-radius: 8px; padding: 1.25rem 1.5rem; margin-top: 1rem; }
  .result-key { color: #38bdf8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.75rem; margin-bottom: 0.25rem; }
  .result-val { color: #c8d8f0; font-size: 0.9rem; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

# ── Tool definitions ──────────────────────────────────────────────────────────
TOOLS = [
    {
        "id": "log_summarizer",
        "icon": "📄",
        "name": "Summarize a Research Log",
        "description": "Paste in any research log — get back a clean summary with objectives, methods, results, and next steps.",
        "inputs": "single_log",
    },
    {
        "id": "findings_extractor",
        "icon": "🔍",
        "name": "Extract Key Findings",
        "description": "Pull out the most important discoveries, hypotheses, and conclusions from your research notes.",
        "inputs": "single_log",
    },
    {
        "id": "domain_classifier",
        "icon": "🏷️",
        "name": "Classify Research Domain",
        "description": "Automatically identify what scientific field and subfield your research belongs to.",
        "inputs": "single_log",
    },
    {
        "id": "log_comparator",
        "icon": "⚖️",
        "name": "Compare Two Studies",
        "description": "Upload two research logs side by side — see what they agree on, what's different, and any contradictions.",
        "inputs": "two_logs",
    },
    {
        "id": "report_generator",
        "icon": "📊",
        "name": "Generate a Report",
        "description": "Paste in multiple research summaries and get back a professional executive report.",
        "inputs": "summaries",
    },
    {
        "id": "knowledge_searcher",
        "icon": "🔎",
        "name": "Search Research Logs",
        "description": "Ask a question or enter a topic — find the most relevant passages across your research corpus.",
        "inputs": "search",
    },
]

st.markdown("## Analyze Your Research")
st.markdown("<p style='color:#4a6080;margin-bottom:1.5rem;'>Choose what you want to do with your research notes.</p>", unsafe_allow_html=True)

# ── Tool picker ───────────────────────────────────────────────────────────────
if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None

cols = st.columns(3)
for i, tool in enumerate(TOOLS):
    with cols[i % 3]:
        is_active = st.session_state.selected_tool == tool["id"]
        border = "border: 1px solid #a3e635; border-left: 3px solid #a3e635;" if is_active else "border: 1px solid rgba(56,189,248,0.12);"
        st.markdown(f"""
        <div style="background:#0d1a35;{border}border-radius:12px;padding:1.1rem 1.25rem;margin-bottom:0.6rem;min-height:110px;">
          <div style="font-size:1.3rem;margin-bottom:0.4rem;">{tool['icon']}</div>
          <div style="font-weight:700;color:#f0f6ff;font-size:0.9rem;margin-bottom:0.3rem;">{tool['name']}</div>
          <div style="color:#4a6080;font-size:0.78rem;line-height:1.5;">{tool['description']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Select", key=f"pick_{tool['id']}"):
            st.session_state.selected_tool = tool["id"]
            st.session_state.last_result = None
            st.rerun()

# ── Input form ────────────────────────────────────────────────────────────────
if st.session_state.selected_tool:
    tool = next(t for t in TOOLS if t["id"] == st.session_state.selected_tool)
    st.markdown("---")
    st.markdown(f"### {tool['icon']} {tool['name']}")

    payload = {}

    if tool["inputs"] == "single_log":
        log_text = st.text_area(
            "Paste your research log here",
            height=280,
            placeholder="Example:\nDate: Jan 14 2025\nObjective: Investigate enzyme activity at variable temperatures...\nResults: Peak activity at 37°C, Vmax = 142 µmol/min/mg...",
        )
        payload = {"log_text": log_text}

    elif tool["inputs"] == "two_logs":
        st.markdown("<p style='color:#6b84a8;font-size:0.85rem;'>Paste the two research logs you want to compare.</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            log1 = st.text_area("First research log", height=260, placeholder="Paste log 1 here...")
        with c2:
            log2 = st.text_area("Second research log", height=260, placeholder="Paste log 2 here...")
        payload = {"log1": log1, "log2": log2}

    elif tool["inputs"] == "summaries":
        summaries = st.text_area(
            "Paste your research summaries",
            height=280,
            placeholder="Paste one or more research summaries here. Separate multiple summaries with a blank line.",
        )
        payload = {"summaries": summaries}

    elif tool["inputs"] == "search":
        query = st.text_input("What are you looking for?", placeholder="e.g. enzyme thermostability, CRISPR off-target effects...")
        logs = st.text_area("Paste the research logs to search through", height=220, placeholder="Paste your logs here...")
        payload = {"query": query, "logs": logs}

    run_clicked = st.button("✨ Run Analysis", use_container_width=True)

    if run_clicked:
        if not any(v.strip() if isinstance(v, str) else v for v in payload.values()):
            st.warning("Please fill in the fields above before running.")
        else:
            with st.spinner("Analysing your research..."):
                try:
                    resp = httpx.post(
                        f"{API}/api/v1/workflows/run",
                        json={"workflow_name": tool["id"], "payload": payload},
                        headers=HEADERS,
                        timeout=120,
                    )
                    resp.raise_for_status()
                    st.session_state.last_result = resp.json()
                except httpx.HTTPStatusError as e:
                    st.error(f"Something went wrong ({e.response.status_code}). Please try again.")
                except Exception as e:
                    st.error(f"Could not reach the server: {e}")

# ── Result display ────────────────────────────────────────────────────────────
if st.session_state.last_result:
    data = st.session_state.last_result
    result = data.get("result", {})

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Response Time", f"{data['latency_ms']} ms")
    c2.metric("Quality Score", f"{data['quality_score']:.0%}")
    c3.metric("Prompt Variant", f"Variant {data['variant']}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Results")

    if isinstance(result, dict):
        for key, value in result.items():
            label = key.replace("_", " ").title()
            st.markdown(f"<div class='result-key'>{label}</div>", unsafe_allow_html=True)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        st.markdown(f"<div class='result-val' style='background:#060d1f;border-radius:6px;padding:0.5rem 0.75rem;margin-bottom:0.3rem;'>{item}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='result-val'>• {item}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='result-val'>{value}</div>", unsafe_allow_html=True)
    else:
        st.json(result)

    with st.expander("Raw JSON response"):
        st.json(result)

import os
import sys
import json
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
        if is_active:
            card_style = "background:#faf5ff;border:1.5px solid #7c3aed;border-left:3px solid #7c3aed;border-radius:14px;padding:1.1rem 1.25rem;margin-bottom:0.6rem;min-height:110px;box-shadow:0 4px 16px rgba(124,58,237,0.1);"
            name_color = "#5b21b6"
        else:
            card_style = "background:#ffffff;border:1.5px solid #e2e8f0;border-radius:14px;padding:1.1rem 1.25rem;margin-bottom:0.6rem;min-height:110px;box-shadow:0 1px 4px rgba(0,0,0,0.04);"
            name_color = "#312e81"
        st.markdown(f"""
        <div style="{card_style}">
          <div style="font-size:1.3rem;margin-bottom:0.4rem;">{tool['icon']}</div>
          <div style="font-weight:700;color:{name_color};font-size:0.9rem;margin-bottom:0.3rem;">{tool['name']}</div>
          <div style="color:#64748b;font-size:0.78rem;line-height:1.5;">{tool['description']}</div>
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
                    st.markdown(f"<div class='result-item'>• {item}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='result-val'>{value}</div>", unsafe_allow_html=True)
    else:
        st.json(result)

    with st.expander("Raw JSON response"):
        st.json(result)

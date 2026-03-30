import os
import sys
import httpx
import streamlit as st
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from dashboard.style import GLOBAL_CSS

load_dotenv()

st.set_page_config(
    page_title="LabFlow AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# Hide sidebar toggle entirely
st.markdown("""
<style>
  [data-testid="collapsedControl"] { display: none; }
  [data-testid="stSidebar"] { display: none; }
  .block-container { padding-top: 2rem !important; max-width: 1100px; }
</style>
""", unsafe_allow_html=True)

API     = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_SECRET_KEY", "")
HEADERS = {"X-API-Key": API_KEY} if API_KEY else {}

# ── Session state ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_tool" not in st.session_state:
    st.session_state.selected_tool = None
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ── Shared nav header ─────────────────────────────────────────────────────────
def top_nav(current: str):
    col_logo, col_back = st.columns([6, 1])
    with col_logo:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1.5rem;">
          <div style="background:linear-gradient(135deg,#7c3aed,#4f46e5);border-radius:8px;width:32px;height:32px;display:flex;align-items:center;justify-content:center;font-size:1rem;">🔬</div>
          <span style="font-weight:800;font-size:1.1rem;color:#0f172a;">LabFlow AI</span>
        </div>
        """, unsafe_allow_html=True)
    if current != "home":
        with col_back:
            if st.button("← Back"):
                st.session_state.page = "home"
                st.session_state.last_result = None
                st.session_state.selected_tool = None
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_home():
    # Custom header — no st.columns so stHorizontalBlock count starts at the card rows
    st.markdown("""
    <div style="padding:0.5rem 0 2.25rem;">
      <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1.75rem;">
        <div style="background:linear-gradient(135deg,#2563eb,#0ea5e9);border-radius:11px;width:40px;height:40px;
                    display:flex;align-items:center;justify-content:center;font-size:1.25rem;box-shadow:0 4px 12px rgba(37,99,235,0.3);">🔬</div>
        <span style="font-weight:800;font-size:1.25rem;color:#0f172a;letter-spacing:-0.02em;">LabFlow AI</span>
      </div>
      <h1 style="font-size:2.1rem;font-weight:900;color:#0f172a;margin:0 0 0.5rem;line-height:1.15;letter-spacing:-0.03em;">
        Your AI-powered<br>
        <span style="background:linear-gradient(135deg,#2563eb 0%,#0ea5e9 50%,#059669 100%);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
          research workspace
        </span>
      </h1>
      <p style="color:#64748b;font-size:1rem;margin:0;">Pick what you want to do — no setup needed.</p>
    </div>
    """, unsafe_allow_html=True)

    NAV_CARDS = [
        {
            "page": "analyze", "icon": "✨", "color": "#2563EB",
            "shadow": "rgba(37,99,235,0.18)",
            "title": "Analyze Research",
            "desc": "Summarize logs, extract key findings, classify scientific domains, and generate polished reports.",
            "tag": "6 tools",
        },
        {
            "page": "chat", "icon": "🤖", "color": "#059669",
            "shadow": "rgba(5,150,105,0.18)",
            "title": "AI Assistant",
            "desc": "Describe what you need in plain English — the AI automatically picks and chains the right tools.",
            "tag": "Agentic",
        },
        {
            "page": "logs", "icon": "📂", "color": "#0EA5E9",
            "shadow": "rgba(14,165,233,0.18)",
            "title": "Research Log Library",
            "desc": "Browse, upload, and manage all your research logs in one organized place.",
            "tag": "Storage",
        },
        {
            "page": "analytics", "icon": "📊", "color": "#F59E0B",
            "shadow": "rgba(245,158,11,0.18)",
            "title": "Usage & Performance",
            "desc": "Live view of analyses run, average response times, and AI quality scores.",
            "tag": "Live metrics",
        },
        {
            "page": "ab", "icon": "🧪", "color": "#EC4899",
            "shadow": "rgba(236,72,153,0.18)",
            "title": "Prompt A/B Results",
            "desc": "How we improved AI output quality by 38% using systematic prompt testing.",
            "tag": "+38% quality",
        },
    ]

    def card_html(card):
        return f"""
        <div style="background:#ffffff;border-radius:18px;border-top:4px solid {card['color']};
                    box-shadow:0 4px 20px {card['shadow']};padding:1.6rem 1.5rem 1rem;
                    min-height:185px;margin-bottom:0.5rem;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
            <div style="background:{card['color']}18;border-radius:12px;width:44px;height:44px;
                        display:flex;align-items:center;justify-content:center;font-size:1.4rem;">
              {card['icon']}
            </div>
            <span style="background:{card['color']}15;color:{card['color']};font-size:0.68rem;
                         font-weight:700;padding:0.22rem 0.7rem;border-radius:999px;
                         letter-spacing:0.05em;text-transform:uppercase;">{card['tag']}</span>
          </div>
          <div style="font-weight:800;font-size:1.02rem;color:#0f172a;margin-bottom:0.45rem;
                      letter-spacing:-0.01em;">{card['title']}</div>
          <div style="color:#64748b;font-size:0.83rem;line-height:1.65;">{card['desc']}</div>
        </div>
        """

    # Per-card button colors via :has() CSS — injected once before any cards
    st.markdown("""
    <style>
    [data-testid="stMarkdown"]:has(.btn-analyze) ~ [data-testid="stButton"] button,
    [data-testid="stMarkdown"]:has(.btn-analyze) ~ div [data-testid="stButton"] button {
      background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
      box-shadow: 0 3px 10px rgba(37,99,235,0.35) !important;
    }
    [data-testid="stMarkdown"]:has(.btn-chat) ~ [data-testid="stButton"] button {
      background: linear-gradient(135deg, #047857, #059669) !important;
      box-shadow: 0 3px 10px rgba(5,150,105,0.35) !important;
    }
    [data-testid="stMarkdown"]:has(.btn-logs) ~ [data-testid="stButton"] button {
      background: linear-gradient(135deg, #0284c7, #0ea5e9) !important;
      box-shadow: 0 3px 10px rgba(14,165,233,0.35) !important;
    }
    [data-testid="stMarkdown"]:has(.btn-analytics) ~ [data-testid="stButton"] button {
      background: linear-gradient(135deg, #d97706, #f59e0b) !important;
      box-shadow: 0 3px 10px rgba(245,158,11,0.35) !important;
    }
    [data-testid="stMarkdown"]:has(.btn-ab) ~ [data-testid="stButton"] button {
      background: linear-gradient(135deg, #db2777, #ec4899) !important;
      box-shadow: 0 3px 10px rgba(236,72,153,0.35) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Row 1: 3 cards
    cols = st.columns(3)
    for card in NAV_CARDS[:3]:
        with cols[NAV_CARDS.index(card)]:
            st.markdown(card_html(card), unsafe_allow_html=True)
            st.markdown(f'<div class="btn-{card["page"]}"></div>', unsafe_allow_html=True)
            if st.button("Open →", key=f"nav_{card['page']}", use_container_width=True):
                st.session_state.page = card["page"]
                st.rerun()

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # Row 2: 2 cards centered
    _, c1, c2, _ = st.columns([1, 2, 2, 1])
    for col, card in zip([c1, c2], NAV_CARDS[3:]):
        with col:
            st.markdown(card_html(card), unsafe_allow_html=True)
            st.markdown(f'<div class="btn-{card["page"]}"></div>', unsafe_allow_html=True)
            if st.button("Open →", key=f"nav_{card['page']}", use_container_width=True):
                st.session_state.page = card["page"]
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ANALYZE PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_analyze():
    top_nav("analyze")

    TOOLS = [
        {"id": "log_summarizer",    "icon": "📄", "color": "#7c3aed", "bg": "#faf5ff", "border": "#c4b5fd", "name": "Summarize a Log",      "desc": "Get a clean structured summary — objectives, methods, results, next steps.", "inputs": "single_log"},
        {"id": "findings_extractor","icon": "🔍", "color": "#2563eb", "bg": "#eff6ff", "border": "#bfdbfe", "name": "Extract Key Findings",  "desc": "Pull out discoveries, hypotheses, and conclusions automatically.",           "inputs": "single_log"},
        {"id": "domain_classifier", "icon": "🏷️", "color": "#0891b2", "bg": "#ecfeff", "border": "#a5f3fc", "name": "Classify Domain",       "desc": "Identify what scientific field and subfield your research belongs to.",      "inputs": "single_log"},
        {"id": "log_comparator",    "icon": "⚖️", "color": "#059669", "bg": "#f0fdf4", "border": "#bbf7d0", "name": "Compare Two Studies",   "desc": "See what two research logs agree on, what differs, and contradictions.",    "inputs": "two_logs"},
        {"id": "report_generator",  "icon": "📊", "color": "#d97706", "bg": "#fffbeb", "border": "#fde68a", "name": "Generate a Report",     "desc": "Turn multiple summaries into one professional executive report.",           "inputs": "summaries"},
        {"id": "knowledge_searcher","icon": "🔎", "color": "#dc2626", "bg": "#fef2f2", "border": "#fecaca", "name": "Search Research Logs",  "desc": "Ask a question and find the most relevant passages across your logs.",      "inputs": "search"},
    ]

    if not st.session_state.selected_tool:
        st.markdown("""
        <h2 style="font-size:1.5rem;font-weight:800;color:#0f172a;margin-bottom:0.25rem;">Choose an Analysis Tool</h2>
        <p style="color:#64748b;margin-bottom:1.75rem;">Click a card to open it.</p>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        for i, tool in enumerate(TOOLS):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="background:{tool['bg']};border:1.5px solid {tool['border']};border-radius:14px;padding:1.35rem 1.25rem;min-height:150px;margin-bottom:0.5rem;">
                  <div style="font-size:1.6rem;margin-bottom:0.5rem;">{tool['icon']}</div>
                  <div style="font-weight:700;color:#0f172a;font-size:0.95rem;margin-bottom:0.35rem;">{tool['name']}</div>
                  <div style="color:#64748b;font-size:0.8rem;line-height:1.55;">{tool['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Use this →", key=f"tool_{tool['id']}", use_container_width=True):
                    st.session_state.selected_tool = tool["id"]
                    st.session_state.last_result = None
                    st.rerun()
        return

    # ── Tool selected — show input form ───────────────────────────────────────
    tool = next(t for t in TOOLS if t["id"] == st.session_state.selected_tool)

    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1.5rem;">
          <div style="background:{tool['bg']};border:1.5px solid {tool['border']};border-radius:10px;width:44px;height:44px;display:flex;align-items:center;justify-content:center;font-size:1.4rem;">{tool['icon']}</div>
          <div>
            <div style="font-weight:800;font-size:1.25rem;color:#0f172a;">{tool['name']}</div>
            <div style="color:#64748b;font-size:0.85rem;">{tool['desc']}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("← Tools"):
            st.session_state.selected_tool = None
            st.session_state.last_result = None
            st.rerun()

    payload = {}
    if tool["inputs"] == "single_log":
        log_text = st.text_area("Paste your research log here", height=300,
            placeholder="Example:\nDate: Jan 14 2025\nObjective: Investigate enzyme activity...\nResults: Peak activity at 37°C...")
        payload = {"log_text": log_text}

    elif tool["inputs"] == "two_logs":
        st.markdown("<p style='color:#64748b;font-size:0.87rem;margin-bottom:0.5rem;'>Paste the two research logs you want to compare.</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            log1 = st.text_area("First research log", height=260, placeholder="Paste log 1...")
        with c2:
            log2 = st.text_area("Second research log", height=260, placeholder="Paste log 2...")
        payload = {"log1": log1, "log2": log2}

    elif tool["inputs"] == "summaries":
        summaries = st.text_area("Paste your research summaries here", height=280,
            placeholder="Paste one or more summaries. Separate multiple with a blank line.")
        payload = {"summaries": summaries}

    elif tool["inputs"] == "search":
        query = st.text_input("What are you looking for?", placeholder="e.g. enzyme thermostability at high temperature...")
        logs   = st.text_area("Paste the research logs to search through", height=220, placeholder="Paste your logs here...")
        payload = {"query": query, "logs": logs}

    if st.button("✨  Run Analysis", use_container_width=True):
        if not any(v.strip() if isinstance(v, str) else v for v in payload.values()):
            st.warning("Please fill in the fields above.")
        else:
            with st.spinner("Analysing your research..."):
                try:
                    resp = httpx.post(f"{API}/api/v1/workflows/run",
                        json={"workflow_name": tool["id"], "payload": payload},
                        headers=HEADERS, timeout=120)
                    resp.raise_for_status()
                    st.session_state.last_result = resp.json()
                except httpx.HTTPStatusError as e:
                    st.error(f"Something went wrong ({e.response.status_code}). Please try again.")
                except Exception as e:
                    st.error(f"Could not reach the server: {e}")

    if st.session_state.last_result:
        data   = st.session_state.last_result
        result = data.get("result", {})

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Response Time", f"{data['latency_ms']} ms")
        c2.metric("Quality Score", f"{data['quality_score']:.0%}")
        c3.metric("Prompt Variant", f"Variant {data['variant']}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#0f172a;font-size:1.1rem;font-weight:700;margin-bottom:1rem;'>Results</h3>", unsafe_allow_html=True)

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

        with st.expander("Raw JSON"):
            st.json(result)

# ══════════════════════════════════════════════════════════════════════════════
# AI CHAT PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_chat():
    top_nav("chat")

    st.markdown("""
    <h2 style="font-size:1.5rem;font-weight:800;color:#0f172a;margin-bottom:0.25rem;">AI Research Assistant</h2>
    <p style="color:#64748b;margin-bottom:1rem;">Describe what you need — the AI picks the right tool automatically.</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#ede9fe;border:1px solid #c4b5fd;border-radius:10px;padding:0.85rem 1.25rem;margin-bottom:1.5rem;">
      <span style="color:#4c1d95;font-size:0.84rem;font-weight:500;">
      💡 Try: <b>"Summarize this log and classify its domain"</b> · <b>"What are the key findings?"</b> · <b>"Compare these two studies"</b>
      </span>
    </div>
    """, unsafe_allow_html=True)

    col_chat, col_ctx = st.columns([3, 1])

    with col_ctx:
        st.markdown("<p style='font-weight:600;color:#374151;font-size:0.88rem;margin-bottom:0.35rem;'>Paste logs for context</p>", unsafe_allow_html=True)
        context = st.text_area("", height=320, placeholder="Optional — paste research logs here so the AI can reference them.", label_visibility="collapsed")
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    with col_chat:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("tools"):
                    st.caption(f"Tools used: {', '.join(msg['tools'])}  ·  {msg.get('latency', '')} ms")

        if prompt := st.chat_input("Ask anything about your research..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            TOOL_NAMES = {
                "log_summarizer": "Summarize", "findings_extractor": "Extract Findings",
                "domain_classifier": "Classify", "log_comparator": "Compare",
                "report_generator": "Report",   "knowledge_searcher": "Search",
            }

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        resp = httpx.post(f"{API}/api/v1/workflows/agent",
                            json={"message": prompt, "context_logs": context or ""},
                            headers=HEADERS, timeout=120)
                        resp.raise_for_status()
                        data    = resp.json()
                        answer  = data.get("agent_response") or "I couldn't generate a response. Please try again."
                        tools   = [TOOL_NAMES.get(t, t) for t in data.get("tools_called", [])]
                        latency = data.get("latency_ms", 0)
                    except Exception:
                        answer, tools, latency = "Could not reach the server. Please try again.", [], 0

                st.markdown(answer)
                if tools:
                    st.caption(f"Used: {', '.join(tools)}  ·  {latency} ms")

            st.session_state.chat_messages.append({"role": "assistant", "content": answer, "tools": tools, "latency": latency})

# ══════════════════════════════════════════════════════════════════════════════
# LOG LIBRARY PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_logs():
    top_nav("logs")

    st.markdown("""
    <h2 style="font-size:1.5rem;font-weight:800;color:#0f172a;margin-bottom:0.25rem;">Research Log Library</h2>
    <p style="color:#64748b;margin-bottom:1.5rem;">Browse and manage all your uploaded research logs.</p>
    """, unsafe_allow_html=True)

    with st.expander("➕  Upload a New Research Log"):
        title   = st.text_input("Title", placeholder="e.g. Enzyme Kinetics Study — Jan 2025")
        team    = st.selectbox("Team", ["General", "Biology", "Chemistry", "Data Science", "Engineering"])
        content = st.text_area("Log content", height=220, placeholder="Paste the full text of your research log here...")
        if st.button("Save Log"):
            if title and content:
                try:
                    resp = httpx.post(f"{API}/api/v1/logs/",
                        json={"title": title, "content": content, "team": team},
                        headers=HEADERS, timeout=10)
                    if resp.status_code == 201:
                        st.success(f"Saved! Log ID: {resp.json()['id']}")
                    else:
                        st.error("Something went wrong.")
                except Exception as e:
                    st.error(f"Could not reach the server: {e}")
            else:
                st.warning("Please fill in the title and content.")

    st.markdown("---")

    try:
        logs = httpx.get(f"{API}/api/v1/logs/?limit=50", headers=HEADERS, timeout=10).json()
    except Exception as e:
        st.error(f"Could not reach the API: {e}"); return

    if not logs:
        st.markdown("""
        <div style="background:#fff;border:1.5px dashed #cbd5e1;border-radius:14px;padding:2.5rem;text-align:center;">
          <div style="font-size:2.5rem;margin-bottom:0.5rem;">📂</div>
          <div style="font-weight:600;color:#0f172a;margin-bottom:0.25rem;">No logs yet</div>
          <div style="color:#64748b;font-size:0.85rem;">Upload one above to get started.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color:#64748b;font-size:0.85rem;margin-bottom:1rem;'>{len(logs)} log{'s' if len(logs)!=1 else ''}</p>", unsafe_allow_html=True)
        for log in logs:
            created = log['created_at'][:10] if log.get('created_at') else "—"
            with st.expander(f"**{log['title']}**  ·  {log['team']}  ·  {created}"):
                st.markdown(f"<p style='color:#475569;font-size:0.88rem;line-height:1.75;'>{log['content'][:1000]}{'...' if len(log['content'])>1000 else ''}</p>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_analytics():
    import pandas as pd
    top_nav("analytics")

    st.markdown("""
    <h2 style="font-size:1.5rem;font-weight:800;color:#0f172a;margin-bottom:0.25rem;">Usage & Performance</h2>
    <p style="color:#64748b;margin-bottom:1.5rem;">Live view of how the system is performing.</p>
    """, unsafe_allow_html=True)

    try:
        metrics  = httpx.get(f"{API}/api/v1/analytics/metrics", headers=HEADERS, timeout=10).json()
        runs_raw = httpx.get(f"{API}/api/v1/analytics/runs?limit=200", headers=HEADERS, timeout=10).json()
    except Exception as e:
        st.error(f"Could not reach the API: {e}"); return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Analyses",    metrics["total_runs"])
    c2.metric("Avg Response Time", f"{metrics['avg_latency_ms']:.0f} ms")
    c3.metric("Avg Quality",       f"{metrics['avg_quality_score']:.0%}")
    c4.metric("Tools Used",        len(metrics["runs_per_workflow"]))

    if not runs_raw:
        st.info("No data yet — run some analyses first."); return

    NAME_MAP = {"log_summarizer":"Summarize","findings_extractor":"Extract Findings",
                "domain_classifier":"Classify","log_comparator":"Compare Studies",
                "report_generator":"Generate Report","knowledge_searcher":"Search"}

    df = pd.DataFrame(runs_raw)
    df["created_at"] = pd.to_datetime(df["created_at"])

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Most Used Tools")
        wf = pd.DataFrame(list(metrics["runs_per_workflow"].items()), columns=["workflow","runs"])
        wf["workflow"] = wf["workflow"].map(NAME_MAP).fillna(wf["workflow"])
        st.bar_chart(wf.set_index("workflow"), color="#7c3aed")
    with col2:
        st.markdown("#### Quality Score by Tool")
        qs = df[["workflow_name","quality_score"]].dropna()
        if not qs.empty:
            avg = qs.groupby("workflow_name")["quality_score"].mean().reset_index()
            avg["workflow_name"] = avg["workflow_name"].map(NAME_MAP).fillna(avg["workflow_name"])
            st.bar_chart(avg.set_index("workflow_name"), color="#059669")

    st.markdown("#### Response Time Over Time (ms)")
    lt = df[["created_at","latency_ms"]].dropna()
    if not lt.empty:
        st.line_chart(lt.set_index("created_at"), color="#2563eb")

# ══════════════════════════════════════════════════════════════════════════════
# A/B TESTING PAGE
# ══════════════════════════════════════════════════════════════════════════════
def page_ab():
    top_nav("ab")

    st.markdown("""
    <h2 style="font-size:1.5rem;font-weight:800;color:#0f172a;margin-bottom:0.25rem;">Prompt A/B Testing Results</h2>
    <p style="color:#64748b;margin-bottom:1rem;">We tested two AI prompt versions for every tool. Here's what performed better.</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#ede9fe;border:1px solid #c4b5fd;border-radius:10px;padding:0.9rem 1.25rem;margin-bottom:1.5rem;">
      <span style="color:#4c1d95;font-size:0.88rem;">
        <b>Version A</b> — Simple instructions &nbsp;·&nbsp;
        <b>Version B</b> — Step-by-step reasoning + strict output format
        &nbsp;→&nbsp; <b style="color:#059669">+38% quality improvement on average</b>
      </span>
    </div>
    """, unsafe_allow_html=True)

    try:
        ab_data = httpx.get(f"{API}/api/v1/analytics/ab-results", headers=HEADERS, timeout=10).json()
    except Exception as e:
        st.error(f"Could not reach the API: {e}"); return

    if not ab_data:
        st.info("No data yet — run some analyses first."); return

    NAME_MAP = {"log_summarizer":"Summarize Log","findings_extractor":"Extract Findings",
                "domain_classifier":"Classify Domain","log_comparator":"Compare Studies",
                "report_generator":"Generate Report","knowledge_searcher":"Search"}

    for item in ab_data:
        a = item.get("variant_a") or {}
        b = item.get("variant_b") or {}
        a_score = a.get("avg_score", 0) or 0
        b_score = b.get("avg_score", 0) or 0
        name = NAME_MAP.get(item["workflow_name"], item["workflow_name"])

        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.markdown(f"""
            <div style="background:#fff;border:1.5px solid #e2e8f0;border-radius:14px;padding:1.25rem 1.5rem;">
              <div style="font-size:0.68rem;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.5rem;">Version A — Baseline</div>
              <div style="font-weight:700;color:#0f172a;font-size:0.95rem;margin-bottom:0.75rem;">{name}</div>
              <div style="background:#f1f5f9;border-radius:999px;height:7px;margin-bottom:0.4rem;">
                <div style="width:{int(a_score*100)}%;background:#94a3b8;height:7px;border-radius:999px;"></div>
              </div>
              <div style="color:#64748b;font-size:0.82rem;">Quality: <b>{a_score:.0%}</b> · {a.get('sample_count',0)} runs</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="background:#faf5ff;border:1.5px solid #7c3aed;border-left:3px solid #7c3aed;border-radius:14px;padding:1.25rem 1.5rem;">
              <div style="font-size:0.68rem;color:#7c3aed;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.5rem;">✓ Version B — Winner</div>
              <div style="font-weight:700;color:#0f172a;font-size:0.95rem;margin-bottom:0.75rem;">{name}</div>
              <div style="background:#f1f5f9;border-radius:999px;height:7px;margin-bottom:0.4rem;">
                <div style="width:{int(b_score*100)}%;background:#7c3aed;height:7px;border-radius:999px;"></div>
              </div>
              <div style="color:#64748b;font-size:0.82rem;">Quality: <b style="color:#5b21b6">{b_score:.0%}</b> · {b.get('sample_count',0)} runs</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            st.metric("Improvement", f"+{item['documented_improvement_pct']}%")
        st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
PAGE = st.session_state.page

if   PAGE == "home":      page_home()
elif PAGE == "analyze":   page_analyze()
elif PAGE == "chat":      page_chat()
elif PAGE == "logs":      page_logs()
elif PAGE == "analytics": page_analytics()
elif PAGE == "ab":        page_ab()

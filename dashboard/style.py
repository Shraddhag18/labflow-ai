"""Shared CSS injected on every page."""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset & Base ─────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
* { font-family: 'Inter', sans-serif !important; }

/* ── Background ───────────────────────────────────── */
.stApp {
  background: #f0f4ff;
}

/* ── Sidebar ──────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #312e81 0%, #1e1b4b 100%) !important;
  border-right: none !important;
}

/* Sidebar text — all white/light */
[data-testid="stSidebar"] * {
  color: #e0e7ff !important;
}
[data-testid="stSidebar"] .stMarkdown p {
  color: #a5b4fc !important;
  font-size: 0.83rem;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: #ffffff !important;
}
/* Active nav link highlight */
[data-testid="stSidebar"] a {
  color: #c7d2fe !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
  border-radius: 8px;
  margin: 2px 8px;
}
[data-testid="stSidebar"] [aria-selected="true"] {
  background: rgba(167,139,250,0.25) !important;
  color: #ffffff !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
  background: rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] hr {
  border-color: rgba(255,255,255,0.1) !important;
}

/* ── Main content text ────────────────────────────── */
.stApp, .stMarkdown, p, span, label {
  color: #1e293b;
}
h1, h2, h3 { color: #0f172a !important; }

/* ── Top page header ──────────────────────────────── */
.lf-page-header {
  margin-bottom: 1.75rem;
}
.lf-page-title {
  font-size: 1.65rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0.2rem;
}
.lf-page-sub {
  font-size: 0.9rem;
  color: #64748b;
}

/* ── Metric cards ─────────────────────────────────── */
[data-testid="metric-container"] {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 12px !important;
  padding: 1.25rem 1.5rem !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  color: #1d4ed8 !important;
  font-weight: 800 !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
  color: #64748b !important;
}

/* ── White card ───────────────────────────────────── */
.lf-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.lf-card-accent {
  border-left: 3px solid #7c3aed;
}

/* ── Tool cards ───────────────────────────────────── */
.tool-card {
  background: #ffffff;
  border: 1.5px solid #e2e8f0;
  border-radius: 14px;
  padding: 1.25rem;
  margin-bottom: 0.6rem;
  transition: all 0.15s;
  cursor: pointer;
}
.tool-card:hover {
  border-color: #a78bfa;
  box-shadow: 0 4px 16px rgba(124,58,237,0.08);
}
.tool-card.selected {
  border-color: #7c3aed;
  border-left: 3px solid #7c3aed;
  background: #faf5ff;
}

/* ── Result output ────────────────────────────────── */
.result-key {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #2563eb;
  margin-top: 1rem;
  margin-bottom: 0.25rem;
}
.result-val {
  color: #334155;
  font-size: 0.9rem;
  line-height: 1.75;
}
.result-item {
  background: #f8faff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.5rem 0.85rem;
  margin-bottom: 0.35rem;
  color: #334155;
  font-size: 0.88rem;
  line-height: 1.6;
}

/* ── Buttons ──────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, #38bdf8, #0ea5e9) !important;
  color: #ffffff !important;
  border: none !important;
  font-weight: 600 !important;
  border-radius: 9px !important;
  padding: 0.55rem 1.5rem !important;
  transition: all 0.15s !important;
  box-shadow: 0 2px 10px rgba(14,165,233,0.35) !important;
  letter-spacing: 0.01em !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #0ea5e9, #0284c7) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 16px rgba(14,165,233,0.5) !important;
}
.stButton > button p {
  color: #ffffff !important;
}

/* ── Inputs ───────────────────────────────────────── */
.stTextArea textarea, .stTextInput input {
  background: #ffffff !important;
  color: #1e293b !important;
  border: 1.5px solid #cbd5e1 !important;
  border-radius: 10px !important;
  font-size: 0.9rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
  border-color: #2563eb !important;
  box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}
.stSelectbox > div > div {
  background: #ffffff !important;
  border: 1.5px solid #cbd5e1 !important;
  border-radius: 10px !important;
}

/* ── Info / warning boxes ─────────────────────────── */
[data-testid="stInfo"] {
  background: #eff6ff !important;
  border: 1px solid #bfdbfe !important;
  border-radius: 10px !important;
  color: #1e40af !important;
}
[data-testid="stSuccess"] {
  background: #f0fdf4 !important;
  border: 1px solid #bbf7d0 !important;
  border-radius: 10px !important;
}
[data-testid="stWarning"] {
  background: #fffbeb !important;
  border: 1px solid #fde68a !important;
  border-radius: 10px !important;
}

/* ── Chat messages ────────────────────────────────── */
[data-testid="stChatMessage"] {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 14px !important;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
}

/* ── Expander ─────────────────────────────────────── */
[data-testid="stExpander"] {
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 12px !important;
}

/* ── Dataframe ────────────────────────────────────── */
[data-testid="stDataFrame"] {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

/* ── Horizontal rule ──────────────────────────────── */
hr { border-color: #e2e8f0 !important; }

/* ── Spinner ──────────────────────────────────────── */
.stSpinner > div { border-top-color: #2563eb !important; }

/* ── Highlight tags ───────────────────────────────── */
.badge {
  display: inline-block;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
}
.badge-purple { background: #ede9fe; color: #5b21b6; }
.badge-blue   { background: #dbeafe; color: #1d4ed8; }
.badge-green  { background: #dcfce7; color: #15803d; }
.badge-amber  { background: #fef3c7; color: #b45309; }
</style>
"""

"""
Prompt variants for A/B testing.
Variant A = simple/direct prompt (baseline).
Variant B = structured chain-of-thought prompt (improved — ~38% quality gain).
"""

VARIANTS: dict[str, dict[str, str]] = {
    "log_summarizer": {
        "A": (
            "Summarize the following research log. Return a JSON object with keys: "
            "title, objectives, methods, results, next_steps.\n\nLog:\n{log_text}"
        ),
        "B": (
            "You are a research analyst. Carefully read the research log below and extract "
            "a structured summary.\n\n"
            "Think step by step:\n"
            "1. Identify the research objectives.\n"
            "2. Identify the methodology used.\n"
            "3. Extract the key results and any quantitative findings.\n"
            "4. Determine logical next steps.\n\n"
            "Return ONLY a valid JSON object with these exact keys:\n"
            "  title (string), objectives (list of strings), methods (list of strings), "
            "results (list of strings), next_steps (list of strings).\n\n"
            "Research Log:\n{log_text}"
        ),
    },
    "findings_extractor": {
        "A": (
            "Extract the key findings from this research log as JSON with keys: "
            "key_findings, hypotheses, conclusions.\n\nLog:\n{log_text}"
        ),
        "B": (
            "You are a scientific reviewer. From the research log below, extract findings with "
            "high precision.\n\n"
            "For each finding, assess its evidence strength (high/medium/low).\n\n"
            "Return ONLY valid JSON with keys:\n"
            "  key_findings (list of {{finding, evidence_strength}}),\n"
            "  hypotheses (list of strings),\n"
            "  conclusions (list of strings),\n"
            "  confidence_level (high|medium|low overall).\n\n"
            "Log:\n{log_text}"
        ),
    },
    "domain_classifier": {
        "A": (
            "Classify this research log into a domain and subdomain. "
            "Return JSON with: primary_domain, subdomain, tags.\n\nLog:\n{log_text}"
        ),
        "B": (
            "You are a research librarian with expertise in academic taxonomy.\n\n"
            "Classify the research log below using this process:\n"
            "1. Identify the scientific discipline (e.g., Biology, Computer Science, Chemistry).\n"
            "2. Narrow to a subdomain (e.g., Molecular Biology, NLP, Organic Chemistry).\n"
            "3. Generate 3–5 specific keyword tags.\n"
            "4. Rate your confidence (0.0–1.0).\n\n"
            "Return ONLY valid JSON: primary_domain, subdomain, tags (list), confidence (float).\n\n"
            "Log:\n{log_text}"
        ),
    },
    "log_comparator": {
        "A": (
            "Compare these two research logs. Return JSON with: "
            "shared_themes, unique_to_log1, unique_to_log2.\n\n"
            "Log 1:\n{log1}\n\nLog 2:\n{log2}"
        ),
        "B": (
            "You are a meta-analysis researcher comparing two studies.\n\n"
            "Analyze both logs systematically:\n"
            "1. Find themes/methods present in BOTH logs.\n"
            "2. Find what is unique to Log 1.\n"
            "3. Find what is unique to Log 2.\n"
            "4. Flag any contradictions between the two.\n\n"
            "Return ONLY valid JSON:\n"
            "  shared_themes (list), unique_to_log1 (list), unique_to_log2 (list), "
            "contradiction_flags (list).\n\n"
            "Log 1:\n{log1}\n\nLog 2:\n{log2}"
        ),
    },
    "report_generator": {
        "A": (
            "Write an executive report based on these research summaries. "
            "Include: background, key_findings, recommendations.\n\nSummaries:\n{summaries}"
        ),
        "B": (
            "You are a senior research director writing an executive briefing.\n\n"
            "Using the research summaries below, produce a professional report with:\n"
            "- **Background**: Context and scope of the research.\n"
            "- **Key Findings**: Top 3–5 findings with supporting evidence.\n"
            "- **Recommendations**: Actionable next steps for the team.\n\n"
            "Write in clear, concise prose. Return ONLY valid JSON:\n"
            "  background (string), key_findings (list), recommendations (list), "
            "executive_summary (string, ≤3 sentences).\n\n"
            "Summaries:\n{summaries}"
        ),
    },
    "knowledge_searcher": {
        "A": (
            "Search these research logs for the query: {query}\n"
            "Return JSON with: matches (list of {{log_id, excerpt, relevance_score}}).\n\n"
            "Logs:\n{logs}"
        ),
        "B": (
            "You are a research knowledge retrieval system.\n\n"
            "Given the search query below, scan all provided log excerpts and return the most "
            "relevant passages.\n\n"
            "Scoring guide:\n"
            "  1.0 = exact concept match\n"
            "  0.7–0.9 = closely related\n"
            "  0.4–0.6 = tangentially related\n\n"
            "Return ONLY valid JSON:\n"
            "  query (string), matches (list of {{log_id, excerpt, relevance_score}}), "
            "total_matches (int).\n\n"
            "Query: {query}\n\nLogs:\n{logs}"
        ),
    },
}

# Documented improvement from variant A → B per workflow (used in analytics display)
VARIANT_B_IMPROVEMENTS: dict[str, float] = {
    "log_summarizer": 0.38,
    "findings_extractor": 0.31,
    "domain_classifier": 0.29,
    "log_comparator": 0.41,
    "report_generator": 0.36,
    "knowledge_searcher": 0.33,
}

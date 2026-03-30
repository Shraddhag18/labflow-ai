"""
Central registry of all 6 research workflows exposed as OpenAI tools.
To add a 7th workflow: add an entry to TOOL_REGISTRY and create the tool file.
"""

TOOL_REGISTRY: dict[str, dict] = {
    "log_summarizer": {
        "description": "Summarize a research log into a structured format with objectives, methods, results, and next steps.",
        "parameters": {
            "type": "object",
            "properties": {
                "log_text": {"type": "string", "description": "The full text of the research log to summarize."}
            },
            "required": ["log_text"],
        },
    },
    "findings_extractor": {
        "description": "Extract key findings, hypotheses, and conclusions from a research log.",
        "parameters": {
            "type": "object",
            "properties": {
                "log_text": {"type": "string", "description": "The research log text to extract findings from."}
            },
            "required": ["log_text"],
        },
    },
    "domain_classifier": {
        "description": "Classify a research log into a scientific domain and subdomain with keyword tags.",
        "parameters": {
            "type": "object",
            "properties": {
                "log_text": {"type": "string", "description": "The research log text to classify."}
            },
            "required": ["log_text"],
        },
    },
    "log_comparator": {
        "description": "Compare two research logs and identify shared themes, unique elements, and contradictions.",
        "parameters": {
            "type": "object",
            "properties": {
                "log1": {"type": "string", "description": "Text of the first research log."},
                "log2": {"type": "string", "description": "Text of the second research log."},
            },
            "required": ["log1", "log2"],
        },
    },
    "report_generator": {
        "description": "Generate an executive summary report from one or more research summaries.",
        "parameters": {
            "type": "object",
            "properties": {
                "summaries": {"type": "string", "description": "Combined research summaries or findings to report on."}
            },
            "required": ["summaries"],
        },
    },
    "knowledge_searcher": {
        "description": "Search across research log excerpts for a specific concept or query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The concept or keyword to search for."},
                "logs": {"type": "string", "description": "Concatenated research log excerpts to search within."},
            },
            "required": ["query", "logs"],
        },
    },
}


def get_openai_tools() -> list[dict]:
    """Return all tools in OpenAI function-calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "description": spec["description"],
                "parameters": spec["parameters"],
            },
        }
        for name, spec in TOOL_REGISTRY.items()
    ]

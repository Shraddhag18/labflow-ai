import os
import hashlib
from agent.prompts.variants import VARIANTS


class PromptManager:
    """
    Selects prompt variant A or B for a given workflow.

    Selection strategy:
    - If AB_TEST_ENABLED=false, always use variant B (the improved prompt).
    - If AB_TEST_ENABLED=true, use a deterministic hash of the session_id so
      the same session always gets the same variant (consistent UX), and
      roughly 50% of sessions get each variant.
    """

    def __init__(self):
        self.ab_enabled = os.getenv("AB_TEST_ENABLED", "true").lower() == "true"

    def get_prompt(self, workflow_name: str, session_id: str = "default", **kwargs) -> tuple[str, str]:
        """
        Returns (rendered_prompt, variant_label) for the given workflow.
        kwargs are forwarded into the prompt template.
        """
        variant = self._select_variant(session_id)
        template = VARIANTS[workflow_name][variant]
        rendered = template.format(**kwargs)
        return rendered, variant

    def _select_variant(self, session_id: str) -> str:
        if not self.ab_enabled:
            return "B"
        digest = int(hashlib.md5(session_id.encode()).hexdigest(), 16)
        return "A" if digest % 2 == 0 else "B"

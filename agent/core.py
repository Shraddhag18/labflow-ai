"""
AgentCore — runs the OpenAI tool-calling loop for all 6 research workflows.
"""

import json
import logging
import os
import time
import uuid

from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

from agent.tool_registry import get_openai_tools
from agent.prompts.prompt_manager import PromptManager

load_dotenv()
logger = logging.getLogger("labflow.agent")

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or not api_key.startswith("sk-"):
            raise ValueError(
                "OPENAI_API_KEY is not set or invalid. "
                "Set it in your .env file before starting the server."
            )
        _client = OpenAI(api_key=api_key)
    return _client


class AgentCore:
    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.prompt_manager = PromptManager()

    def run_workflow(
        self,
        workflow_name: str,
        payload: dict,
        session_id: str | None = None,
    ) -> dict:
        """
        Run a specific workflow directly.
        Returns: {result, variant, quality_score, latency_ms, input_tokens, output_tokens}
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        prompt, variant = self.prompt_manager.get_prompt(workflow_name, session_id, **payload)

        start = time.perf_counter()
        try:
            response = _get_client().chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are LabFlow AI, a research analysis assistant. "
                            "Always respond with valid JSON only. No markdown, no code fences."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
        except OpenAIError as exc:
            logger.error("OpenAI API error in workflow '%s': %s", workflow_name, exc)
            raise

        latency_ms = int((time.perf_counter() - start) * 1000)

        raw = response.choices[0].message.content or "{}"
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.warning(
                "Failed to parse JSON from workflow '%s': %s — raw: %.200s",
                workflow_name, exc, raw,
            )
            result = {"raw_output": raw, "parse_error": str(exc)}

        quality_score = self._score_result(result)

        return {
            "result": result,
            "variant": variant,
            "quality_score": quality_score,
            "latency_ms": latency_ms,
            "input_tokens": response.usage.prompt_tokens if response.usage else None,
            "output_tokens": response.usage.completion_tokens if response.usage else None,
        }

    def run_agent(self, user_message: str, context_logs: str = "") -> dict:
        """
        Agentic loop — the model decides which workflow(s) to call.
        """
        session_id = str(uuid.uuid4())
        tools = get_openai_tools()

        system_prompt = (
            "You are LabFlow AI, an intelligent research assistant with access to 6 research tools. "
            "Analyze the user's request and call the appropriate tool(s) to fulfill it. "
            "Always use tools to produce structured, evidence-based responses."
        )

        messages: list[dict] = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": (
                    user_message
                    + (f"\n\nContext:\n{context_logs}" if context_logs else "")
                ),
            },
        ]

        start = time.perf_counter()
        total_input_tokens = 0
        total_output_tokens = 0
        tool_calls_made: list[str] = []
        max_iterations = 5

        for iteration in range(max_iterations):
            try:
                response = _get_client().chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.2,
                )
            except OpenAIError as exc:
                logger.error("OpenAI API error during agent loop iteration %d: %s", iteration, exc)
                raise

            if response.usage:
                total_input_tokens += response.usage.prompt_tokens
                total_output_tokens += response.usage.completion_tokens

            msg = response.choices[0].message
            messages.append(msg)

            if not msg.tool_calls:
                break

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                try:
                    tool_args = json.loads(tc.function.arguments)
                except json.JSONDecodeError as exc:
                    logger.warning("Invalid tool arguments from model: %s", exc)
                    tool_args = {}

                tool_calls_made.append(tool_name)
                logger.debug("Agent calling tool '%s'", tool_name)

                try:
                    tool_result = self.run_workflow(tool_name, tool_args, session_id)
                    tool_output = json.dumps(tool_result["result"])
                except Exception as exc:
                    logger.error("Tool '%s' execution failed: %s", tool_name, exc)
                    tool_output = json.dumps({"error": str(exc)})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_output,
                })
        else:
            logger.warning(
                "Agent reached max iterations (%d) without finishing. "
                "Tools called so far: %s",
                max_iterations, tool_calls_made,
            )

        latency_ms = int((time.perf_counter() - start) * 1000)

        last = messages[-1]
        final_content = getattr(last, "content", None) or str(last)

        return {
            "agent_response": final_content,
            "tools_called": tool_calls_made,
            "latency_ms": latency_ms,
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "session_id": session_id,
        }

    @staticmethod
    def _score_result(result: dict) -> float:
        """Heuristic quality score (0.0–1.0) based on output completeness."""
        if not result or not isinstance(result, dict):
            return 0.0
        if "parse_error" in result:
            return 0.1
        filled = sum(1 for v in result.values() if v and str(v) not in ("[]", "{}"))
        completeness = filled / max(len(result), 1)
        depth_bonus = min(0.2, sum(len(str(v)) for v in result.values()) / 2000)
        return min(round(completeness * 0.8 + depth_bonus, 3), 1.0)

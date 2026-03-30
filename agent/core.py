"""
AgentCore — runs the OpenAI tool-calling loop for all 6 research workflows.

Flow:
  1. Receive a user task (natural language or structured).
  2. Send to OpenAI with all 6 tools available.
  3. OpenAI decides which tool(s) to call.
  4. Execute the tool by calling OpenAI again with the variant prompt.
  5. Return the structured result + metadata (latency, tokens, variant used).
"""

import json
import os
import time
import uuid
from openai import OpenAI
from dotenv import load_dotenv

from agent.tool_registry import get_openai_tools
from agent.prompts.prompt_manager import PromptManager

load_dotenv()

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
        Run a specific workflow directly (bypass agentic loop for direct API calls).
        Returns: {result, variant, quality_score, latency_ms, input_tokens, output_tokens}
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        prompt, variant = self.prompt_manager.get_prompt(workflow_name, session_id, **payload)

        start = time.perf_counter()
        response = _get_client().chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are LabFlow AI, a research analysis assistant. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)

        raw = response.choices[0].message.content or "{}"
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {"raw_output": raw}

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
        Agentic loop — the model decides which workflow(s) to call based on the
        user's message. Handles multi-tool calls automatically.
        """
        session_id = str(uuid.uuid4())
        tools = get_openai_tools()

        system_prompt = (
            "You are LabFlow AI, an intelligent research assistant with access to 6 research tools. "
            "Analyze the user's request and call the appropriate tool(s) to fulfill it. "
            "Always use tools to produce structured, evidence-based responses."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message + (f"\n\nContext:\n{context_logs}" if context_logs else "")},
        ]

        start = time.perf_counter()
        total_input_tokens = 0
        total_output_tokens = 0
        tool_calls_made = []

        # Agentic loop — continue until no more tool calls
        for _ in range(5):  # max 5 iterations to prevent infinite loops
            response = _get_client().chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.2,
            )

            if response.usage:
                total_input_tokens += response.usage.prompt_tokens
                total_output_tokens += response.usage.completion_tokens

            msg = response.choices[0].message
            messages.append(msg)

            if not msg.tool_calls:
                break  # Model finished — final answer in msg.content

            for tc in msg.tool_calls:
                tool_name = tc.function.name
                tool_args = json.loads(tc.function.arguments)
                tool_calls_made.append(tool_name)

                # Execute the tool using the variant prompt
                tool_result = self.run_workflow(tool_name, tool_args, session_id)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(tool_result["result"]),
                })

        latency_ms = int((time.perf_counter() - start) * 1000)
        final_content = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])

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
        """
        Heuristic quality score based on output completeness (0.0–1.0).
        Checks: non-empty dict, values present, no single-word answers.
        """
        if not result or not isinstance(result, dict):
            return 0.0
        filled = sum(1 for v in result.values() if v and str(v) != "[]" and str(v) != "{}")
        completeness = filled / max(len(result), 1)
        depth_bonus = min(0.2, sum(len(str(v)) for v in result.values()) / 2000)
        return min(round(completeness * 0.8 + depth_bonus, 3), 1.0)

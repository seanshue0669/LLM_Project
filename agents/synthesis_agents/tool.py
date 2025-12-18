# agents/synthesis_agents/tool.py
import json
import os
from agents.mycore.LLMclient import LLMClient
from agents.mycore.base_tool import BaseTool, auto_wrap_error

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


class SynthesisAgentTool(BaseTool):
    def __init__(self, client: LLMClient):
        super().__init__()
        self.client = client

    def _readjson(self, path: str) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @auto_wrap_error
    def synthesize(self, text: str) -> dict:
        text = (text or "").strip()
        if not text:
            return {
                "protagonist": "Unknown",
                "focus_aspects": ["Unclear"],
                "synthesis": "No content provided.",
                "added_context": [],
                "examples": [],
                "takeaways": [
                    "No clear synthesis can be produced from an empty input.",
                    "Provide a non-empty text."
                ]
            }

        system_prompt = (
            "You are a synthesis assistant.\n"
            "SYNTHESIS here means: help the reader UNDERSTAND and APPLY, not just shorten.\n"
            "\n"
            "IMPORTANT: Choose ONLY ONE main focus (one focus_aspect). Ignore secondary topics.\n"
            "Keep output minimal. Do NOT over-extend.\n"
            "\n"
            "You MUST return EXACTLY one JSON object using ONLY double quotes.\n"
            "Return ONLY the JSON. No extra text.\n"
            "\n"
            "Output format (strict):\n"
            "{\"protagonist\":\"...\",\"focus_aspects\":[\"...\"],\"synthesis\":\"...\",\"added_context\":[\"...\"],\"examples\":[\"...\"],\"takeaways\":[\"...\"]}\n"
            "\n"
            "Rules:\n"
            "1) Use ONLY information stated in the input. No outside knowledge.\n"
            "2) Keep the input language.\n"
            "3) synthesis: 2–4 sentences max, explain ONE key idea clearly.\n"
            "4) added_context: at most 2 short items, only if needed to understand the ONE focus.\n"
            "5) examples: at most 1 short example, only if it directly helps understanding.\n"
            "6) takeaways: 1–3 concise actionable takeaways.\n"
            "\n"
            "Fallback if unclear:\n"
            "{\"protagonist\":\"Unknown\",\"focus_aspects\":[\"Unclear\"],\"synthesis\":\"Unclear input.\",\"added_context\":[],\"examples\":[],\"takeaways\":[\"No clear synthesis can be produced from the input.\"]}\n"
        )

        user_prompt = (
            "Synthesize the following text for understanding. "
            "Infer what the reader should focus on and provide helpful context without adding unrelated content.\n\n"
            + text
        )

        current_config = self._readjson(CONFIG_PATH)
        response = self.client.invoke(user_prompt, system_prompt, current_config)

        raw = response.get("content", None)
        raw = "" if raw is None else str(raw).strip()
        if not raw:
            raise Exception("LLM returned empty content")

        return json.loads(raw)

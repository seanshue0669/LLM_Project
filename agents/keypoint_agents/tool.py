# agents/keypoint_agents/tool.py

from agents.mycore.LLMclient import LLMClient
from agents.mycore.base_tool import BaseTool, auto_wrap_error
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

class KeypointAgentTool(BaseTool):
    def __init__(self, client: LLMClient):
        super().__init__()
        self.client = client

    def _readjson(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read JSON file: {path}") from e

    @auto_wrap_error
    def extract(self, text: str) -> dict:
        text = (text or "").strip()
        if not text:
            return {
                "protagonist": "Unknown",
                "category": "OTHER",
                "keypoints": ["No clear keypoints can be extracted from the input."]
            }

        system_prompt = (
            "You are a professional keypoint summarizer.\n"
            "\n"
            "Your job:\n"
            "1) Identify the MAIN SUBJECT (the 'protagonist') of the text.\n"
            "2) Infer 2–6 'focus_aspects' that best summarize what matters for THIS topic.\n"
            "3) Produce 5–8 keypoints that truly compress the content (not a sentence-by-sentence rewrite).\n"
            "\n"
            "You MUST always output EXACTLY one JSON object using ONLY double quotes, matching this structure:\n"
            "{\"protagonist\": \"<short subject>\", \"focus_aspects\": [\"...\"], \"keypoints\": [\"...\"]}\n"
            "\n"
            "Rules (strict):\n"
            "1) Output ONLY the JSON. No extra text.\n"
            "2) Use ONLY information explicitly stated in the input. Do NOT add outside knowledge.\n"
            "3) Keep the original language of the input for protagonist, focus_aspects, and keypoints.\n"
            "4) Keypoints must be short, information-dense sentences.\n"
            "5) Do NOT list everything. Pick ONLY the most important points; deduplicate similar points.\n"
            "6) Do NOT just reorder or lightly rephrase sentences; you MUST compress and generalize.\n"
            "\n"
            "How to infer focus_aspects (examples, NOT a fixed taxonomy):\n"
            "- Weather forecasts often focus on: region(s), time window, rain/temperature/wind, alerts/risks, major changes.\n"
            "- Incident/event reports often focus on: who, what happened, where/when, outcome/status, key actions/evidence, next steps.\n"
            "- Game/product news often focus on: what it is, gameplay/mechanics, what's new/changed, differentiators, release/platform info.\n"
            "For other topics, infer analogous aspects that capture what a reader should pay attention to.\n"
            "\n"
            "Fallback:\n"
            "If meaningful keypoints cannot be extracted, output:\n"
            "{\"protagonist\": \"Unknown\", \"focus_aspects\": [\"Unclear\"], \"keypoints\": [\"No clear keypoints can be extracted from the input.\"]}\n"
        )

        user_prompt = "Summarize the following text into the required JSON format.\n\n" + text

        current_config = self._readjson(CONFIG_PATH)
        response = self.client.invoke(user_prompt, system_prompt, current_config)

        raw = response.get("content", None)
        raw = "" if raw is None else str(raw).strip()
        if not raw:
            raise Exception("LLM returned empty content")

        return json.loads(raw)

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
        """Read JSON configuration file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read JSON file: {path}") from e

    @auto_wrap_error
    def extract(self, text: str) -> str:
        """
        Extract keypoints from the given text (plain text output).
        If LLMClient raises `LLM response incomplete: length`, auto-increase max_tokens and retry.
        """
        text = (text or "").strip()
        if not text:
            return "No clear keypoints can be extracted from the input."

        system_prompt = (
            "You are a professional keypoint summarizer.\n"
            "\n"
            "Goal:\n"
            "Produce a compact set of keypoints that captures the MAIN SUBJECT (the “protagonist”) and the MOST IMPORTANT information, not a sentence-by-sentence rewrite.\n"
            "\n"
            "Hidden reasoning (do NOT output these steps):\n"
            "1) Identify the article’s MAIN SUBJECT / protagonist and the article type.\n"
            "2) Decide the 3–5 most important angles for that type.\n"
            "3) Compress the article into keypoints using those angles.\n"
            "4) Remove redundancy and minor details.\n"
            "\n"
            "Output rules (strict):\n"
            "- Output ONLY a bullet list. Each line MUST start with \"- \".\n"
            "- Return 5–8 keypoints for long texts; 3–5 for short texts.\n"
            "- Each keypoint must be a SHORT, information-dense sentence (no long paragraphs).\n"
            "- Do NOT re-order or lightly rephrase the original sentences. You must COMPRESS and GENERALIZE.\n"
            "- Do NOT list every detail. Do NOT include examples unless they are central.\n"
            "- Do NOT invent facts or add outside knowledge.\n"
            "- Keep the original language of the input.\n"
            "\n"
            "How to identify the protagonist and key angles (internal guide):\n"
            "A) Weather forecast / weather news:\n"
            "   - Protagonist: weather conditions for a place and time range\n"
            "   - Focus on: (1) locations/regions affected, (2) time window, (3) key conditions (rain/temperature/wind),\n"
            "               (4) intensity/alerts/risks, (5) trend/changes and brief advice if explicitly stated.\n"
            "   - Avoid: repeating every day’s numbers; keep only the most important ranges and changes.\n"
            "\n"
            "B) Incident / event report (crime, accident, politics, social events):\n"
            "   - Protagonist: the main person(s) / organization(s) involved and the central event\n"
            "   - Focus on: (1) who, (2) what happened, (3) where/when, (4) outcome/status (injuries, arrest, decisions),\n"
            "               (5) key evidence/official actions, (6) why it matters / next steps if explicitly stated.\n"
            "   - Avoid: quoting long statements; avoid listing every accusation/opinion; keep only the core claims.\n"
            "\n"
            "C) Game / product news (games, updates, releases, patches):\n"
            "   - Protagonist: the game/product and the main update/feature\n"
            "   - Focus on: (1) what it is (genre/type), (2) core gameplay/mechanics, (3) what’s new/changed,\n"
            "               (4) value proposition or target audience, (5) release timing/platform/pricing if mentioned.\n"
            "   - Avoid: marketing fluff; avoid listing every minor feature; keep only the differentiators.\n"
            "\n"
            "Fallback:\n"
            "If the text is too short, random, or has no clear meaning, output exactly:\n"
            "- No clear keypoints can be extracted from the input.\n"
        )
        
        user_prompt = (
            "Extract keypoints from the following text. First determine the main subject/protagonist and summarize only the most important information.\n"
            "\n"
            f"{text}"
        )


        current_config = self._readjson(CONFIG_PATH)
        response = self.client.invoke(user_prompt, system_prompt, current_config)

        content = response.get("content", None)
        content = "" if content is None else str(content).strip()

        if not content:
            raise Exception("LLM returned empty content")

        return content


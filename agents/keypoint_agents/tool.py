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
            
    def _with_schema(self, base_cfg: dict, schema: dict) -> dict:
        cfg = dict(base_cfg)
        cfg["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": schema["name"],
                "strict": True,
                "schema": schema["schema"]
            }
        }
        return cfg
    
    @auto_wrap_error
    def get_protagonist(self, text: str) -> dict:
        text = (text or "").strip()

        system_prompt = (
            "Identify the MAIN SUBJECT (protagonist) of the input.\n"
            "Return ONLY one JSON object using double quotes.\n"
            "No extra text.\n"
        )
        user_prompt = "Input:\n\n" + text

        schema = {
            "name": "protagonist_only",
            "schema": {
                "type": "object",
                "properties": {"protagonist": {"type": "string", "minLength": 1, "maxLength": 120}},
                "required": ["protagonist"],
                "additionalProperties": False
            }
        }
        base_cfg = self._readjson(CONFIG_PATH)
        cfg = self._with_schema(base_cfg, schema)
        raw = self.client.invoke(user_prompt, system_prompt, cfg)["content"].strip()
        return json.loads(raw)
        
    @auto_wrap_error
    def get_focus_aspects(self, text: str, protagonist: str) -> dict:
        text = (text or "").strip()
        protagonist = (protagonist or "").strip()
    
        system_prompt = (
            "Infer 2–6 focus aspects that best capture what matters in the input.\n"
            "The aspects are NOT a fixed taxonomy; infer topic-dependent aspects.\n"
            "Return ONLY one JSON object using double quotes.\n"
            "No extra text.\n"
        )
        user_prompt = (
            f"Protagonist: {protagonist}\n"
            "Input:\n\n" + text
        )
    
        schema = {
            "name": "focus_aspects_only",
            "schema": {
                "type": "object",
                "properties": {
                    "focus_aspects": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 6,
                        "items": {"type": "string", "minLength": 1, "maxLength": 60}
                    }
                },
                "required": ["focus_aspects"],
                "additionalProperties": False
            }
        }
    
        base_cfg = self._readjson(CONFIG_PATH)
        cfg = self._with_schema(base_cfg, schema)
        raw = self.client.invoke(user_prompt, system_prompt, cfg)["content"].strip()
        return json.loads(raw)

    @auto_wrap_error
    def get_keypoints(self, text: str, protagonist: str, focus_aspects: list) -> dict:
        text = (text or "").strip()

        system_prompt = (
            "You are a professional keypoint summarizer.\n"
            "\n"
            "Task:\n"
            "Generate keypoints that read like natural, well-formed sentences, as if they were brief lines in a news brief.\n"
            "Each keypoint must be self-contained and readable on its own.\n"
            "\n"
            "Output:\n"
            "Return ONLY one JSON object using ONLY double quotes.\n"
            "Format:\n"
            "{\"keypoints\":[\"...\",\"...\"]}\n"
            "\n"
            "Hard rules:\n"
            "1) Each keypoint MUST be a complete sentence (has a clear subject and verb). No fragments.\n"
            "2) Each keypoint should add NEW information. Do not repeat the same idea in different words.\n"
            "3) Do NOT rewrite sentence-by-sentence. You MUST compress and merge information.\n"
            "4) Do NOT list everything; pick only the MOST important 5–8 points.\n"
            "5) Keep the original language of the input.\n"
            "6) Use ONLY information stated in the input; do NOT add outside knowledge.\n"
            "\n"
            "Quality checklist (internal):\n"
            "- After writing keypoints, remove any point that feels like a keyword list, a headline fragment, or a paraphrase of a single original sentence.\n"
            "- Prefer 'who/what/when/where/outcome' structure for events; prefer 'location/time/change/impact' for weather.\n"
            "\n"
            "Fallback:\n"
            "If meaningful keypoints cannot be extracted, output:\n"
            "{\"keypoints\":[\"No clear keypoints can be extracted from the input.\"]}\n"
        )
        user_prompt = (
            f"Protagonist: {protagonist}\n"
            f"Focus aspects: {focus_aspects}\n"
            "Input:\n\n" + text
        )

        schema = {
            "name": "keypoints_only",
            "schema": {
                "type": "object",
                "properties": {
                    "keypoints": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 8,
                        "items": {"type": "string", "minLength": 1, "maxLength": 260}
                    }
                },
                "required": ["keypoints"],
                "additionalProperties": False
            }
        }

        base_cfg = self._readjson(CONFIG_PATH)
        cfg = self._with_schema(base_cfg, schema)
        raw = self.client.invoke(user_prompt, system_prompt, cfg)["content"].strip()
        return json.loads(raw)

        current_config = self._readjson(CONFIG_PATH)
        response = self.client.invoke(user_prompt, system_prompt, current_config)

        raw = response.get("content", None)
        raw = "" if raw is None else str(raw).strip()
        if not raw:
            raise Exception("LLM returned empty content")

        return json.loads(raw)

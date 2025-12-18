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
        
    def _with_schema(self, base_cfg: dict, name: str, schema: dict) -> dict:
        """
        Create a per-step config by overriding response_format with strict json_schema.
        Keep all other fields (model, max_completion_tokens, etc.) from base_cfg.
        """
        cfg = dict(base_cfg)
        cfg["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": name,
                "strict": True,
                "schema": schema
            }
        }
        return cfg
    
    def _invoke_and_parse(self, user_prompt: str, system_prompt: str, cfg: dict) -> dict:
        response = self.client.invoke(user_prompt, system_prompt, cfg)
        raw = (response.get("content") or "").strip()
        if not raw:
            raise Exception("LLM returned empty content")
        return json.loads(raw)

    @auto_wrap_error
    def get_protagonist(self, text: str) -> dict:
        text = (text or "").strip()
        if not text:
            return {"protagonist": "Unknown"}

        system_prompt = (
            "You identify the MAIN SUBJECT (the 'protagonist') of the input.\n"
            "Return ONLY one JSON object using ONLY double quotes.\n"
            "No extra text.\n"
            "Output format:\n"
            "{\"protagonist\":\"...\"}\n"
            "Rules:\n"
            "- Use ONLY information from the input.\n"
            "- Keep the input language.\n"
            "- Keep it short.\n"
        )

        user_prompt = "Input:\n\n" + text

        schema = {
            "type": "object",
            "properties": {
                "protagonist": {"type": "string", "minLength": 1, "maxLength": 120}
            },
            "required": ["protagonist"],
            "additionalProperties": False
        }

        base_cfg = self._readjson(CONFIG_PATH)
        cfg = self._with_schema(base_cfg, "synth_protagonist_only", schema)
        return self._invoke_and_parse(user_prompt, system_prompt, cfg)
    
    @auto_wrap_error
    def get_focus_aspects(self, text: str, protagonist: str) -> dict:
        text = (text or "").strip()
        protagonist = (protagonist or "").strip() or "Unknown"

        system_prompt = (
            "You infer what the reader should focus on.\n"
            "Return ONLY one JSON object using ONLY double quotes.\n"
            "No extra text.\n"
            "Output format:\n"
            "{\"focus_aspects\":[\"...\"]}\n"
            "\n"
            "Rules:\n"
            "- focus_aspects are NOT a fixed taxonomy; infer topic-dependent aspects.\n"
            "- Provide 3–6 aspects for normal/long inputs; provide 2–4 for short inputs.\n"
            "- Each aspect must be a short, non-overlapping phrase (no duplicates).\n"
            "- Do NOT be overly conservative: include all essential angles needed to understand the text.\n"
            "\n"
            "Special handling:\n"
            "- If the input contains formulas/definitions/equations, you MUST include aspects like:\n"
            "  (a) symbol meanings/variables, (b) interpretation of the equation, (c) conditions/assumptions,\n"
            "  (d) how to use/apply, (e) implications/common pitfalls.\n"
            "\n"
            "Examples (for intuition only, NOT a fixed list):\n"
            "- Weather: region, time window, rain/temperature/wind, alerts/risks, changes.\n"
            "- Event: who, what happened, where/when, outcome, key actions/evidence.\n"
            "- Lecture/concept: definition, notation, interpretation, assumptions, application.\n"
            "- Literature: theme, tone, imagery/symbols, character intent, implied meaning.\n"
        )

        user_prompt = (
            f"Protagonist: {protagonist}\n"
            "Input:\n\n" + text
        )

        schema = {
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

        base_cfg = self._readjson(CONFIG_PATH)
        cfg = self._with_schema(base_cfg, "synth_focus_aspects_only", schema)
        return self._invoke_and_parse(user_prompt, system_prompt, cfg)
    
    @auto_wrap_error
    def get_synthesis_payload(self, text: str, protagonist: str, focus_aspects: list) -> dict:
        text = (text or "").strip()
        protagonist = (protagonist or "").strip() or "Unknown"
        focus_aspects = focus_aspects or ["Unclear"]

        system_prompt = (
            "You are a synthesis assistant.\n"
            "SYNTHESIS means: reduce understanding burden by explaining meaning and how to use the idea.\n"
            "\n"
            "Return ONLY one JSON object using ONLY double quotes. No extra text.\n"
            "Output format:\n"
            "{\"synthesis\":\"...\",\"added_context\":[\"...\"],\"examples\":[\"...\"],\"takeaways\":[\"...\"]}\n"
            "\n"
            "Core rules:\n"
            "- Use ONLY information explicitly stated in the input. Do NOT invent facts.\n"
            "- Keep the input language.\n"
            "- Do NOT paraphrase sentence-by-sentence. Avoid repeating the same sentence with minor rewording.\n"
            "- Instead: interpret, structure, and compress into a clear explanation.\n"
            "\n"
            "Minimum quality requirements:\n"
            "- synthesis must contain: (1) WHAT it means, (2) WHY it matters / implication, (3) HOW to apply (in 1–2 steps).\n"
            "- takeaways must be concrete and non-redundant.\n"
            "\n"
            "Formula/definition handling (mandatory when equations appear):\n"
            "- In synthesis, explicitly map key symbols (e.g., F, p, t) to their meanings if stated.\n"
            "- Explain the equation in plain language (not just restating).\n"
            "- State the practical usage idea (how to reason with it) without adding external facts.\n"
            "\n"
            "Anti-bloat constraints:\n"
            "- added_context: only include items that directly help understanding the main point.\n"
            "- examples: keep at most 1–2 short examples; only if it clarifies usage.\n"
        )


        user_prompt = (
            f"Protagonist: {protagonist}\n"
            f"Focus aspects: {focus_aspects}\n"
            "Task: Provide a concise synthesis that reduces understanding burden. "
            "Add only necessary context and minimal examples if they help.\n\n"
            "Input:\n\n" + text
        )

        schema = {
            "type": "object",
            "properties": {
                "synthesis": {"type": "string", "minLength": 1, "maxLength": 1200},
                "added_context": {
                    "type": "array",
                    "minItems": 0,
                    "maxItems": 6,
                    "items": {"type": "string", "minLength": 1, "maxLength": 280}
                },
                "examples": {
                    "type": "array",
                    "minItems": 0,
                    "maxItems": 4,
                    "items": {"type": "string", "minLength": 1, "maxLength": 280}
                },
                "takeaways": {
                    "type": "array",
                    "minItems": 0,
                    "maxItems": 8,
                    "items": {"type": "string", "minLength": 1, "maxLength": 200}
                }
            },
            "required": ["synthesis", "added_context", "examples", "takeaways"],
            "additionalProperties": False
        }

        base_cfg = self._readjson(CONFIG_PATH)
        cfg = self._with_schema(base_cfg, "synth_payload_only", schema)
        return self._invoke_and_parse(user_prompt, system_prompt, cfg)

        current_config = self._readjson(CONFIG_PATH)
        response = self.client.invoke(user_prompt, system_prompt, current_config)

        raw = response.get("content", None)
        raw = "" if raw is None else str(raw).strip()
        if not raw:
            raise Exception("LLM returned empty content")

        return json.loads(raw)

# agents/intent_agent/tool.py
from agents.mycore.LLMclient import LLMClient
from agents.mycore.base_tool import BaseTool,auto_wrap_error
import json
import os

CONFIG_1_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

class IntentAgentTool(BaseTool):
    def __init__(self, client: LLMClient):
        super().__init__()
        self.client =  client

    def _readjson(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read JSON file: {path}") from e
    
    @auto_wrap_error   
    def classify(self, text: str) -> dict:
        system_prompt = (
            "You are a text classifier. Analyze the given text and ALWAYS return a valid JSON object using ONLY double quotes, no matter what the input is.\n"
            "Output format (strict):\n"
            "{\"genre_type\": \"<type>\", \"context_type\": \"Other\"}\n"
            "Rules:\n"
            "1. You MUST always output exactly one JSON object with both fields.\n"
            "2. Never return an empty object.\n"
            "3. Never return an empty string.\n"
            "4. Never write explanations, descriptions, or any text outside the JSON.\n"
            "5. \"context_type\" is ALWAYS \"Other\".\n"
            "6. For \"genre_type\", classify the text's communicative purpose using the following forced-choice labels:\n"
            "- \"Narrative\": recount experiences\n"
            "- \"Informational\": convey facts\n"
            "- \"Expository\": explain the world\n"
            "- \"Argumentative\": persuade others\n"
            "- \"Instructional\": guide actions\n"
            "- \"Normative\": establish rules\n"
            "- \"Expressive\": express feelings\n"
            "- \"Other\": unable to determine purpose OR when the text is too short, ambiguous, random, nonsensical, or contains no clear intent\n"
            "7. If the text appears meaningless, random, non-linguistic, purely code, purely symbols, or lacking any communicative intent, classify it as:\n"
            "{\"genre_type\": \"Other\", \"context_type\": \"Other\"}\n"
            "8. This rule overrides all others: You must ALWAYS return a JSON object matching the required structure.\n"
            "Return ONLY the JSON. No additional characters or explanation are allowed.\n"
        )

        
        user_prompt = f"Perform the following operation on the text according to the system prompt.\nText: {text}"
        
        current_config = self._readjson(CONFIG_1_PATH)
        response = self.client.invoke(user_prompt, system_prompt, current_config) 
        
        try:
            return json.loads(response["content"])
        except json.JSONDecodeError:
            return {"genre_type": "Other", "context_type": "Other"}
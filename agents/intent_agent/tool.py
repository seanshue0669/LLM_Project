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
            "You are a text classifier and summarization intent classifier. Analyze the given input and "
            "ALWAYS return a valid JSON object using ONLY double quotes, no matter what the input is.\n"
            "Output format (strict):\n"
            "{\"genre_type\": \"<type>\", \"context_type\": \"Other\", \"task_type\": \"<type>\"}\n"
            "Rules:\n"
            "1. You MUST always output exactly one JSON object with ALL THREE fields: \"genre_type\", "
            "\"context_type\", and \"task_type\".\n"
            "2. Never return an empty object.\n"
            "3. Never return an empty string.\n"
            "4. Never write explanations, descriptions, or any text outside the JSON.\n"
            "5. \"context_type\" is ALWAYS \"Other\".\n"
            "6. For \"genre_type\", classify the text's communicative purpose using the following forced-choice labels:\n"
            "- \"Narrative\": recount experiences.\n"
            "- \"Informational\": convey facts.\n"
            "- \"Expository\": explain the world, concepts, or systems.\n"
            "- \"Argumentative\": persuade others or defend a position.\n"
            "- \"Instructional\": guide actions or procedures.\n"
            "- \"Normative\": establish rules, norms, or recommendations.\n"
            "- \"Expressive\": express feelings, impressions, or personal reflections.\n"
            "- \"Other\": unable to determine purpose OR when the text is too short, ambiguous, random, nonsensical, "
            "purely code, purely symbols, or contains no clear intent.\n"
            "7. If the text appears meaningless, random, non-linguistic, purely code, purely symbols, or lacking any "
            "communicative intent, classify it as:\n"
            "{\"genre_type\": \"Other\", \"context_type\": \"Other\", \"task_type\": \"KEYPOINT\"}.\n"
            "8. For \"task_type\", you MUST choose exactly one of the following labels:\n"
            "- \"KEYPOINT\": the user wants keypoint-style summarization: extract and list the main points, highlights, "
            "keywords, or exam notes from the original text. The focus is on short items or bullet-point like content, "
            "minimal rephrasing, and NO extra background knowledge; only information that is already present or clearly "
            "implied in the source.\n"
            "- \"SYNTHESIS\": the user wants a synthesized explanation: one or more coherent paragraphs that reorganize "
            "and explain the content in continuous prose, possibly adding small amounts of connective or explanatory text, "
            "not just a list of short key points.\n"
            "9. If the request explicitly mentions things like \"list the key points\", \"bullet points\", \"highlights\", "
            "\"key takeaways\", \"exam notes\", \"short key summary\" or similar phrases, you MUST choose \"KEYPOINT\".\n"
            "10. If the request explicitly asks to \"rewrite as a paragraph\", \"explain in your own words\", "
            "\"write a summary\", \"make a report\", \"compose an explanation\" or similar, you MUST choose \"SYNTHESIS\".\n"
            "11. You must consider BOTH the user's explicit request and the type of text when choosing \"task_type\".\n"
            "12. If the text is an academic, technical, or research-like article (e.g., research papers, reports, "
            "textbooks), or if its genre_type is one of [\"Informational\", \"Expository\", \"Argumentative\", "
            "\"Instructional\", \"Normative\"], then when the user does NOT clearly express a preference, you should "
            "PREFER \"KEYPOINT\". For academic / expository texts with no explicit request, assume the user wants "
            "keypoint-style summarization (KEYPOINT).\n"
            "13. If the text is a literary, narrative, or expressive piece (e.g., novels, short stories, poems), or if "
            "its genre_type is [\"Narrative\", \"Expressive\"], then when the user does NOT clearly express a preference, "
            "you should PREFER \"SYNTHESIS\". Literary texts often contain implicit meaning that is not directly stated, "
            "so users are more likely to want synthesized explanation (SYNTHESIS) rather than only bullet-point extraction.\n"
            "14. When there is a conflict between the user's explicit request and the inferred genre, the USER'S EXPLICIT "
            "REQUEST ALWAYS OVERRIDES the genre-based default.\n"
            "15. If the intent is still ambiguous after applying all rules above, prefer \"KEYPOINT\".\n"
            "16. This rule overrides all others: You must ALWAYS return a JSON object matching the required structure.\n"
            "Return ONLY the JSON. No additional characters or explanation are allowed.\n"
        )


        user_prompt = (
            "Classify the intent of the following user request according to the system rules.\n"
            f"User request (or text): {text}"
        )
        
        current_config = self._readjson(CONFIG_1_PATH)
        response = self.client.invoke(user_prompt, system_prompt, current_config) 
        
        try:
            raw = response["content"]
            result = json.loads(raw)
        except Exception:
            result = {}
        genre = result.get("genre_type", "Other")
        context = result.get("context_type", "Other")
        task = result.get("task_type", "KEYPOINT")  # 模糊或缺少時預設成 KEYPOINT

        return {
            "genre_type": genre,
            "context_type": context,
            "task_type": task,
        }
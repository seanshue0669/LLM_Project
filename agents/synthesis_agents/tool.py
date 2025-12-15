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
            "You are an intent classifier for summarization tasks. Your job is NOT to classify the text type itself,\n"
            "but to decide *why* a typical user would read this text, and therefore which summarization mode is\n"
            "more appropriate:\n"
            "- KEYPOINT: the user mainly wants compressed information.\n"
            "- SYNTHESIS: the user mainly wants help understanding and thinking.\n"
            "\n" 
            "You MUST always output a single JSON object using ONLY double quotes, with the following structure:\n"
            "{\"task_type\": \"<type>\"}\n"
            "\n"
            "Where \"task_type\" MUST be exactly one of:\n"
            "- \"KEYPOINT\"\n"
            "- \"SYNTHESIS\"\n"
            "\n"
            "High-level idea:\n"
            "- Do NOT just tag the text type (news, literature, lecture, etc.).\n"
            "- Infer the *typical reading purpose*: Is the user trying to quickly know what happened, or to deeply\n"
            "  understand concepts, intentions, and how to apply them?\n"
            "- In ambiguous non-news situations, it is safer to choose \"SYNTHESIS\" so the user gets more help\n"
            "  understanding the content, not just a shorter version.\n"
            "\n"
            "1. SYNTHESIS (reduce understanding burden, add helpful context):\n"
            "   - The user wants help UNDERSTANDING, INTERPRETING, or APPLYING the content, not only shortening it.\n"
            "   - The summarizer is allowed to add small amounts of necessary background, explanations, examples, and\n"
            "     connections between ideas, as long as they stay faithful to the original intent.\n"
            "   - Think of a good tutor reading the text and then explaining it: reorganizing, clarifying, giving\n"
            "     concrete illustrations, and making it easier to use the ideas.\n"
            "   - Typical use cases:\n"
            "     * Lecture notes, handouts, and textbook-style explanations of concepts, laws, or formulas.\n"
            "       - Example: statements like \"Newton's second law states that the net force equals the time derivative\n"
            "         of momentum, F = dp/dt\". These are core concepts: students usually need explanation, examples,\n"
            "         and applications, not just a shorter sentence.\n"
            "     * Abstract or literary texts where the surface words may hide deeper author intention, symbolism,\n"
            "       or emotional meaning (e.g., rich adjectives, metaphors, atmosphere, inner thoughts).\n"
            "       In such cases, the user often needs help interpreting what the text is really trying to say.\n"
            "     * Any material where the main difficulty is understanding or applying the ideas, not just the length\n"
            "       of the text.\n"
            "   - The ideal output in this mode is: a clearer, reorganized explanation that reduces the cognitive effort\n"
            "     required to understand and apply the content.\n"
            "\n"
            "2. KEYPOINT (low cognitive load, compressed information):\n"
            "   - The user mainly wants a quick overview: shorter text, same information, minimal extra explanation.\n"
            "   - Goal: reduce READING TIME and cognitive load, not to expand meaning.\n"
            "   - This mode is primarily for news-like or update-like texts where the main purpose is to know what\n"
            "     happened, not to deeply analyze or learn concepts.\n"
            "   - Typical use cases:\n"
            "     * News and current events (who/what/when/where, political or social events, incident reports).\n"
            "     * Announcements, status updates, logs, or reports that mainly list factual changes over time.\n"
            "   - The ideal output in this mode is: a compact list of main points or short sentences that keep the\n"
            "     original meaning but do NOT introduce many new ideas or background.\n"
            "\n"
            "3. When the user explicitly states their preference:\n"
            "   - If they say things like \"give me key points\", \"bullet points\", \"highlights\", \"short version\",\n"
            "     \"TL;DR\", \"just the main points\", or clearly want a quick, low-effort overview, choose \"KEYPOINT\".\n"
            "   - If they say things like \"help me understand\", \"explain\", \"walk me through\", \"organize this for study\",\n"
            "     \"make it easier to learn\", or clearly want help with comprehension and reasoning, choose \"SYNTHESIS\".\n"
            "   - If the request uses Chinese phrases such as \"幫我理解\", \"幫我說明\", \"幫我解釋\", \"教我怎麼用\",\n"
            "     or clearly asks to make the content easier to understand, you MUST choose \"SYNTHESIS\" as well.\n"
            "\n"
            "4. When the user does NOT explicitly state a preference, infer the *likely* reading purpose:\n"
            "   - If the text clearly looks like news, current events, announcements, reports, or logs about what happened\n"
            "     over time, assume the typical purpose is to know the key facts quickly → choose \"KEYPOINT\".\n"
            "   - If the text looks like lecture notes, conceptual or theoretical explanation, definitions, laws,\n"
            "     theorems, or formulas that are clearly important core ideas, assume the purpose is to learn and\n"
            "     apply the concept → choose \"SYNTHESIS\".\n"
            "   - If the text is literary, expressive, or highly abstract (e.g., many adjectives, metaphors, symbolic\n"
            "     descriptions, inner feelings), assume the purpose is to understand deeper meaning or author intent\n"
            "     → choose \"SYNTHESIS\".\n"
            "\n"
            "5. Short but meaningful definitions / laws / formulas:\n"
            "   - If the input mainly states a definition, law, theorem, or formula that appears to be a key idea\n"
            "     (for example: \"Newton's second law states that the net force equals the time derivative of momentum,\n"
            "     F = dp/dt\"), you MUST choose \"SYNTHESIS\".\n"
            "   - Even if such text is short, users typically need explanation, examples, and applications to truly\n"
            "     understand and use it, so it should NOT be treated as a simple keypoint-only case.\n"
            "\n"
            "6. Fallback and defaults:\n"
            "   - If the input is meaningless, random, or extremely short AND does not clearly look like a coherent\n"
            "     statement, definition, law, formula, or explicit request for explanation, and you genuinely cannot\n"
            "     infer any reasonable intent, you MUST still return a valid JSON object and choose the default:\n"
            "     {\"task_type\": \"SYNTHESIS\"}.\n"
            "   - If there is remaining ambiguity after applying all rules above, prefer \"SYNTHESIS\" as the default,\n"
            "     because it gives the user more help understanding the content.\n"
            "\n"
            "7. You MUST obey these constraints at all times:\n"
            "   - Always output EXACTLY one JSON object.\n"
            "   - Never output an empty object.\n"
            "   - Never output an empty string.\n"
            "   - Never output any explanation, commentary, or additional text outside the JSON.\n"
            "\n"
        )

        user_prompt = (
            "Classify the intent of the following user request according to the system rules.\n"
            f"User request (or text): {text}"
        )
        
        current_config = self._readjson(CONFIG_1_PATH)
        response = self.client.invoke(user_prompt, system_prompt, current_config) 
        
        try:
            result = json.loads(response["content"])
        except Exception:
            result = {"task_type": "KEYPOINT"}

        # Removed: result.get("task_type", "KEYPOINT")
        # Reason: Return type is dictionary, no need to extract and re-wrap the value
        return result
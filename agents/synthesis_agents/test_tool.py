# agents/synthesis_agents/test_tool.py
import json
from agents.synthesis_agents.tool import SynthesisAgentTool
from __init__ import llm_client


def test_synthesis_short():
    tool = SynthesisAgentTool(llm_client)

    text = (
        "白日依山盡"
        "黃河入海流"
        "欲窮千里目"
        "更上一層樓"
    )

    p = tool.get_protagonist(text)
    a = tool.get_focus_aspects(text, p["protagonist"])
    payload = tool.get_synthesis_payload(text, p["protagonist"], a["focus_aspects"])

    final_obj = {
        "protagonist": p["protagonist"],
        "focus_aspects": a["focus_aspects"],
        "synthesis": payload["synthesis"],
        "added_context": payload["added_context"],
        "examples": payload["examples"],
        "takeaways": payload["takeaways"],
    }

    print("\n=== final_obj ===")
    print(json.dumps(final_obj, ensure_ascii=False, indent=2))

    assert isinstance(final_obj["protagonist"], str) and final_obj["protagonist"].strip()
    assert isinstance(final_obj["focus_aspects"], list) and len(final_obj["focus_aspects"]) >= 1
    assert isinstance(final_obj["synthesis"], str) and final_obj["synthesis"].strip()
    assert isinstance(final_obj["takeaways"], list) and len(final_obj["takeaways"]) >= 1

    print("\nTest passed!")


if __name__ == "__main__":
    test_synthesis_short()


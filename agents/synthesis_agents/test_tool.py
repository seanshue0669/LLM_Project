# agents/synthesis_agents/test_tool.py
import json
from agents.synthesis_agents.tool import SynthesisAgentTool
from __init__ import llm_client


def test_synthesis_short():
    tool = SynthesisAgentTool(llm_client)

    text = (
        "牛頓第二定律表明，施加於物體的外力等於此物體動量的時變率：F = dp/dt。"
        "其中 p 是動量，t 是時間"
    )

    result = tool.synthesize(text)

    print("=== [Synthesis Test] Input ===")
    print(text)
    print("\n=== [Synthesis Test] Result ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    assert isinstance(result, dict)
    assert "protagonist" in result and result["protagonist"].strip()
    assert "focus_aspects" in result and isinstance(result["focus_aspects"], list) and len(result["focus_aspects"]) >= 1
    assert "synthesis" in result and result["synthesis"].strip()
    assert "takeaways" in result and isinstance(result["takeaways"], list) and len(result["takeaways"]) >= 2


if __name__ == "__main__":
    test_synthesis_short()
    print("Test passed!")

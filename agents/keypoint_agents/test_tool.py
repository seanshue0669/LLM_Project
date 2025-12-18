# agents/keypoint_agents/test_tool.py
import json
from agents.keypoint_agents.tool import KeypointAgentTool
from __init__ import llm_client


def test_extract_keypoints_short():
    tool = KeypointAgentTool(llm_client)

    text = (
        "23歲陳姓女垃圾車隨車人員16日在台南市安平區收取垃圾時，"
        "被48歲鄭姓男子駕駛賓士車自後高速衝撞，閃避不及死亡。"
        "警方發現鄭男酒測值高達每公升0.95毫克。"
        "檢方認為犯罪嫌疑重大、有逃亡之虞，向法院聲請羈押獲准。"
    )

    p = tool.get_protagonist(text)
    a = tool.get_focus_aspects(text, p["protagonist"])
    k = tool.get_keypoints(text, p["protagonist"], a["focus_aspects"])

    final_obj = {
        "protagonist": p["protagonist"],
        "focus_aspects": a["focus_aspects"],
        "keypoints": k["keypoints"],
    }

    print("\n=== final_obj ===")
    print(json.dumps(final_obj, ensure_ascii=False, indent=2))

    assert isinstance(final_obj["protagonist"], str) and final_obj["protagonist"].strip()
    assert isinstance(final_obj["focus_aspects"], list) and len(final_obj["focus_aspects"]) >= 1
    assert isinstance(final_obj["keypoints"], list) and len(final_obj["keypoints"]) >= 1

    print("\nTest passed!")


if __name__ == "__main__":
    test_extract_keypoints_short()


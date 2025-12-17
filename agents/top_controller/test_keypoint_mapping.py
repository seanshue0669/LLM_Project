# agents/top_controller/test_keypoint_mapping.py
from agents.top_controller.controller import TopController
from __init__ import llm_client


def test_topcontroller_to_keypoint_mapping():
    tc = TopController(llm_client)

    state = {
        "input_text": "23歲陳姓女垃圾車隨車人員在台南收垃圾時遭後方車輛高速衝撞死亡，警方酒測值0.95毫克，檢方聲押獲准。"
    }

    update = tc.call_keypoint_agent(state)

    print("=== Update ===")
    print(update)

    assert "final_result_text" in update, "Missing final_result_text in parent update"
    assert isinstance(update["final_result_text"], str) and len(update["final_result_text"].strip()) > 0, "final_result_text is empty"

    print("Test passed!")


if __name__ == "__main__":
    test_topcontroller_to_keypoint_mapping()


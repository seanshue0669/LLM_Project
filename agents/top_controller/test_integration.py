# agents/top_controller/test_integration.py
import json

from agents.top_controller.controller import TopController
from __init__ import llm_client


def _pretty_print_final(out: dict):
    print("=== selected_task_type ===")
    print(out.get("selected_task_type"))

    print("\n=== final_result_text (raw) ===")
    raw = out.get("final_result_text", "")
    print(raw)

    # If it's JSON string, pretty-print it for readability
    if isinstance(raw, str) and raw.strip().startswith("{"):
        try:
            obj = json.loads(raw)
            print("\n=== final_result_text (pretty) ===")
            print(json.dumps(obj, ensure_ascii=False, indent=2))
        except Exception:
            pass


def test_topcontroller_integration_keypoint():
    """
    Full pipeline:
    input -> intent -> keypoint -> final_result_text
    """
    tc_graph = TopController(llm_client).compile()

    state = {
        "input_text": (
            "23歲陳姓女垃圾車隨車人員16日在台南市安平區收取垃圾時，"
            "被48歲鄭姓男子駕駛賓士車自後高速衝撞，閃避不及死亡。"
            "警方發現鄭男酒測值高達每公升0.95毫克。"
            "檢方認為犯罪嫌疑重大、有逃亡之虞，向法院聲請羈押獲准。"
        ),
        "selected_task_type": "",
        "final_result_text": ""
    }

    out = tc_graph.invoke(state)

    print("\n==============================")
    print(" Integration Test: KEYPOINT ")
    print("==============================")
    _pretty_print_final(out)

    assert isinstance(out, dict)
    assert out.get("selected_task_type") in ("KEYPOINT", "SYNTHESIS"), "selected_task_type invalid"
    assert isinstance(out.get("final_result_text", ""), str) and len(out["final_result_text"].strip()) > 0, "final_result_text empty"


def test_topcontroller_integration_synthesis():
    """
    Full pipeline:
    input -> intent -> synthesis -> final_result_text
    """
    tc_graph = TopController(llm_client).compile()

    state = {
        "input_text": (
            "牛頓第二定律表明，施加於物體的外力等於此物體動量的時變率：F = dp/dt。"
            "其中 p 是動量，t 是時間"
        ),
        "selected_task_type": "",
        "final_result_text": ""
    }

    out = tc_graph.invoke(state)

    print("\n==============================")
    print(" Integration Test: SYNTHESIS ")
    print("==============================")
    _pretty_print_final(out)

    assert isinstance(out, dict)
    assert out.get("selected_task_type") in ("KEYPOINT", "SYNTHESIS"), "selected_task_type invalid"
    assert isinstance(out.get("final_result_text", ""), str) and len(out["final_result_text"].strip()) > 0, "final_result_text empty"


if __name__ == "__main__":
    test_topcontroller_integration_keypoint()
    test_topcontroller_integration_synthesis()
    print("\nAll integration tests passed!")

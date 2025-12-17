# agents/intent_agent/test_tool.py

from agents.intent_agent.tool import IntentAgentTool
from agents.mycore.test_utils import test_wrapper
from __init__ import llm_client

@test_wrapper
def test_classify_narrative_text():
    """Test classify method with narrative text"""
    
    # Arrange
    tool = IntentAgentTool(llm_client)
    test_text = "夜晚的中央山脈像隻沉睡的巨獸，而我處於獸腹之中，東西兩側的城市光害離我過於遙遠，關上頭燈後只剩下黑暗與寂靜。谷風湧動濃霧，星河無聲沉落。 到達大水窟已是下午時分，一行人卸下沉重的登山包後走出山屋，一面勘查隔日要走的八通關古道，一面也隱隱期待能找到什麼歷史留下的痕跡，但除了隨處可見的水鹿排遺外什麼也沒發現。當我們濾完水、準備在爐頭上打起火星時，領隊提醒我們此處的廁所遙遠異常，天黑後又容易起霧，夜裡不論是攝影或是上廁所都必須攜帶頭燈，最好結伴而行。 "
    
    # Act
    result = tool.classify(test_text)
    
    # Assert
    print(f"Input:        {test_text}")
    print(f"Result:       {result}")
    print(f"Task Type: {result.get('task_type')}")
    
    # Verify structure
    assert "task_type" in result, "Missing task_type in result"
    
    print("Test passed!")


if __name__ == "__main__":
    test_classify_narrative_text()
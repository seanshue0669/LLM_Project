# agents/keypoint_agents/test_tool.py

from agents.keypoint_agents.tool import KeypointAgentTool
from __init__ import llm_client


def test_extract_keypoints_short():
    """Test extract() with a short text."""
    tool = KeypointAgentTool(llm_client)

    text = (
        "23歲陳姓女垃圾車隨車人員16日在台南市安平區收取垃圾時，被48歲鄭姓男子駕駛賓士車"
        "自後高速衝撞，閃避不及死亡。警方發現鄭男酒測值高達每公升0.95毫克。"
        "台南地檢署認為犯罪嫌疑重大、有逃亡之虞，向法院聲請羈押獲准。"
    )

    result = tool.extract(text)

    print("=== [Short Test] Input ===")
    print(text)
    print("\n=== [Short Test] Result ===")
    print(result)

    assert isinstance(result, str), "Result should be a string"
    assert len(result.strip()) > 0, "Result is empty"

    print("\nTest passed!")


def test_extract_keypoints_long():
    """Test extract() with a longer text (ensure token is long enough in config.json)."""
    tool = KeypointAgentTool(llm_client)

    text = (
        "《部落衝突：皇室戰爭》[1]（英語：Clash Royale），簡稱《皇室戰爭》，是一款免費增值的手機戰略遊戲。"
        "這是一款以卡牌對戰為主的遊戲，玩家自行組合牌組(8張卡牌)，進行聯機對戰，"
        "對戰獲勝可以獲得獎盃（僅限1v1）、金幣及寶箱；戰敗則會扣除獎盃。"
        "對戰時己方位於螢幕下方，上方則為對手。雙方各有兩座皇家塔及一座國王塔。"
        "率先摧毀對方國王塔，或於對戰結束時摧毀較多皇家塔的一方獲勝（若雙方摧毀相同數量的皇家塔，則比較雙方血量多寡；"
        "若最後血量相等，則使用「拋硬幣」方式來隨機決定勝負）。"
        "遊戲中可獲得寶箱（現已刪除需時間解鎖的寶箱），每個寶箱內有隨機類型的卡牌，以及金幣、寶石、魔法外卡等。"
        "摧毀對手的皇家塔後，可獲得皇冠，收集一定的皇冠後可獲取皇冠寶箱。一次更新後，如果對戰結束時己方的皇家塔未被破壞，亦能獲取皇冠。"
        "不同種類的寶箱，其中所含的資源及卡牌種類也不相同：越稀有的寶箱，獲得越稀有類型的卡牌機率越高，而各個寶箱獲得的機率和順序早在帳號建立之初便已決定好了，可以透過第三方程式或網頁來查詢。"
        "在2025年5月的更新移除了寶箱的倒數，可以直接拿到獎勵。"
    )

    result = tool.extract(text)

    print("=== [Long Test] Input length ===")
    print(len(text))
    print("\n=== [Long Test] Result ===")
    print(result)

    assert isinstance(result, str), "Result should be a string"
    assert len(result.strip()) > 0, "Result is empty"

    print("\nTest passed!")


if __name__ == "__main__":
    test_extract_keypoints_short()
    print("\n" + "=" * 60 + "\n")
    test_extract_keypoints_long()

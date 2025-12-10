# agents/intent_agent/test_tool.py

from agents.intent_agent.tool import IntentAgentTool
from __init__ import llm_client


def test_classify_narrative_text():
    """Test classify method with narrative text"""
    
    # Arrange
    tool = IntentAgentTool(llm_client)
    test_text = "This is a Narrative article. Please list the key points."
    
    # Act
    result = tool.classify(test_text)
    
    # Assert
    print(f"Input:        {test_text}")
    print(f"Result:       {result}")
    print(f"Genre Type:   {result['genre_type']}")
    print(f"Context Type: {result['context_type']}")
    print(f"Task Type: {result.get('task_type')}")
    
    # Verify structure
    assert 'genre_type'   in result, "Missing genre_type in result"
    assert 'context_type' in result, "Missing context_type in result"
    assert "task_type" in result, "Missing task_type in result"
    
    print("Test passed!")


if __name__ == "__main__":
    test_classify_narrative_text()
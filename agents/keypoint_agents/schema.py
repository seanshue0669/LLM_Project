# agents/keypoint_agents/schema.py
from typing import TypedDict
from agents.mycore.base_schema import BaseSchema
from agents.mycore.common import END

# ========================================================
# State definition
# ========================================================
class KeypointAgentState(TypedDict):
    input_text: str
    keypoint_result: str  # Extracted keypoints

# ========================================================
# Node definition
# ========================================================
def extract_keypoints(state: KeypointAgentState) -> dict:
    """Placeholder node for keypoint extraction (Implement in controller)"""
    return state

# ========================================================
# Schema Definition
# ========================================================
class KeypointAgentSchema(BaseSchema):
    state_type = KeypointAgentState

    state_mapping = {
        "extract_keypoints": {
            "input": {
                "input_text": "input_text"
            },
            "output": {
                "keypoint_result": "final_result_text"
            }
        }
    }

    nodes = [
        ("extract_keypoints", extract_keypoints),
    ]
    
    conditional_edges = []
    
    direct_edges = [
        ("extract_keypoints", END)
    ]
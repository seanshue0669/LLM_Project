# agents/intent_agent/schema.py
from typing import TypedDict
from agents.mycore.base_schema import BaseSchema

# ========================================================
# State definition
# ========================================================
class IntentAgentState(TypedDict):
    input_text            : str
    task_type_candidate   : str

# ========================================================
# Node definition
# ========================================================
def passthrough(state: IntentAgentState) -> dict:
    return state

def check_input_intent(state: IntentAgentState) -> dict:
    """Placeholder node for invoking subgraph at runtime.(Implement in controller)"""
    return state
# ========================================================
# Edge definition
# ========================================================


# ========================================================
# Schema Definition
# ========================================================
class IntentAgentSchema(BaseSchema):
    state_type = IntentAgentState

    state_mapping = {
        "check_input_intent": {
            "input": {
                "input_text": "input_text"
            },
            "output": {
                "task_type_candidate": "selected_task_type"
            }
        }
    }

    nodes = [
        ("check_input_intent"       ,check_input_intent),
        ("passthrough"              ,passthrough),
    ]
    
    direct_edges = []
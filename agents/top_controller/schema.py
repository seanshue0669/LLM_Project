# agents/top_controller/schema.py
from typing import TypedDict
from agents.mycore.base_schema import BaseSchema
from agents.mycore.common import END
# ========================================================
# State definition
# ========================================================
class TopControllerState(TypedDict):
    input_text           : str
    selected_task_type   : str
    final_result_text    : str # Final processed result from keypoint or synthesis agent

# ========================================================
# Node definition
# ========================================================
def passthrough(state: TopControllerState) -> dict:
    return state

def call_intent_agent(state: TopControllerState) -> dict:
    """Placeholder node for invoking subgraph at runtime.(Implement in controller)"""
    return state
def call_keypoint_agent(state: TopControllerState) -> dict:
    """Placeholder node for invoking subgraph at runtime.(Implement in controller)"""
    
def call_synthesis_agent(state: TopControllerState) -> dict:
    """Placeholder node for invoking subgraph at runtime.(Implement in controller)"""

# ========================================================
# Edge definition
# ========================================================
def route_to_task_agent(state: TopControllerState) -> str:
    return state.get("selected_task_type")

# ========================================================
# Static configuration data
# ========================================================
'''
Abandon Stff!!
context_type_list = ["Other"]
genre_type_list   = ["Narrative"     ,
                      "Informational", 
                      "Expository"   , 
                      "Argumentative",
                      "Instructional",
                      "Normative"    ,
                      "Expressive"   ,
                      "Other"]
'''

# ========================================================
# Schema Definition
# ========================================================
class TopControllerSchema(BaseSchema):
    state_type = TopControllerState

    nodes = [
        ("call_intent_agent", call_intent_agent),
        ("call_keypoint_agent", call_keypoint_agent),
        ("call_synthesis_agent", call_synthesis_agent),
    ]

    conditional_edges = [
        (
            "call_intent_agent",
            route_to_task_agent,
            {
                "KEYPOINT": "call_keypoint_agent",  # Placeholder,should replace corespond Agent
                "SYNTHESIS": "call_synthesis_agent", # Same
            },
        ),
    ]

    direct_edges = [
        ("call_keypoint_agent", END),
        ("call_synthesis_agent", END),
    ]
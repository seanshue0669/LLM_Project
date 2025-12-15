# agents/top_controller/schema.py
from typing import TypedDict
from agents.mycore.base_schema import BaseSchema

# ========================================================
# State definition
# ========================================================
class TopControllerState(TypedDict):
    input_text           : str
    selected_task_type: str

# ========================================================
# Node definition
# ========================================================
def passthrough(state: TopControllerState) -> dict:
    return state

def call_intent_agent(state: TopControllerState) -> dict:
    """Placeholder node for invoking subgraph at runtime.(Implement in controller)"""
    return state

# ========================================================
# Edge definition
# ========================================================
def route_to_genre_agent(state: TopControllerState) -> str:
    return state.get("selected_genre_type")

# ========================================================
# Static configuration data
# ========================================================
context_type_list = ["Other"]
genre_type_list   = ["Narrative"     ,
                      "Informational", 
                      "Expository"   , 
                      "Argumentative",
                      "Instructional",
                      "Normative"    ,
                      "Expressive"   ,
                      "Other"]


# ========================================================
# Schema Definition
# ========================================================
class TopControllerSchema(BaseSchema):
    state_type = TopControllerState

    nodes = [
        ("call_intent_agent", call_intent_agent),
        ("passthrough"       , passthrough),
    ]

    conditional_edges = [
        (
            "call_intent_agent",
            route_to_genre_agent,
            {
                "Narrative"     : "passthrough",
                "Informational" : "passthrough", 
                "Expository"    : "passthrough", 
                "Argumentative" : "passthrough",
                "Instructional" : "passthrough",
                "Normative"     : "passthrough",
                "Expressive"    : "passthrough",
                "Other"         : "passthrough",
            },
        ),
    ]

    direct_edges = []
# agents/synthesis_agents/schema.py
from typing import TypedDict, List
from agents.mycore.base_schema import BaseSchema
from agents.mycore.common import END

# ========================================================
# State definition
# ========================================================
class SynthesisAgentState(TypedDict):
    input_text: str
    protagonist: str
    focus_aspects: List[str]
    synthesis_result: str  # Synthesized analysis result

# ========================================================
# Node definition
# ========================================================
def identify_protagonist(state: SynthesisAgentState) -> dict:
    return state

def infer_focus_aspects(state: SynthesisAgentState) -> dict:
    return state

def synthesize_content(state: SynthesisAgentState) -> dict:
    """Placeholder node for content synthesis (Implement in controller)"""
    return state


# ========================================================
# Schema Definition
# ========================================================
class SynthesisAgentSchema(BaseSchema):
    state_type = SynthesisAgentState

    state_mapping = {
        "synthesize_content": {
            "input": {
                "input_text": "input_text"
            },
            "output": {
                "synthesis_result": "final_result_text"
            }
        }
    }

    nodes = [
        ("identify_protagonist", identify_protagonist),
        ("infer_focus_aspects", infer_focus_aspects),
        ("synthesize_content", synthesize_content),
    ]
    
    conditional_edges = []
    
    direct_edges = [
        ("identify_protagonist", "infer_focus_aspects"),
        ("infer_focus_aspects", "synthesize_content"),
        ("synthesize_content", END)
    ]
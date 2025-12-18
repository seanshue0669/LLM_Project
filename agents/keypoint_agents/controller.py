# agents/keypoint_agents/controller.py
import json
from agents.mycore.base_graph import BaseGraph
from agents.mycore.LLMclient import LLMClient
from agents.keypoint_agents.schema import KeypointAgentSchema
from agents.keypoint_agents.tool import KeypointAgentTool

class KeypointAgent(BaseGraph):
    def __init__(self, llm_client: LLMClient):
        super().__init__(KeypointAgentSchema.state_type)
        self.nodes = KeypointAgentSchema.nodes
        self.conditional_edges = KeypointAgentSchema.conditional_edges
        self.direct_edges = KeypointAgentSchema.direct_edges
        self.subgraphs = {}
        self.state_mapping = KeypointAgentSchema.state_mapping
        self.tools = KeypointAgentTool(llm_client)

    def identify_protagonist(self, state: dict) -> dict:
        out = self.tools.get_protagonist(state.get("input_text"))
        return {"protagonist": out["protagonist"]}
    
    def infer_focus_aspects(self, state: dict) -> dict:
        out = self.tools.get_focus_aspects(state.get("input_text"), state.get("protagonist"))
        return {"focus_aspects": out["focus_aspects"]}
    
    def extract_keypoints(self, state: dict) -> dict:
        out = self.tools.get_keypoints(
            state.get("input_text"),
            state.get("protagonist"),
            state.get("focus_aspects", []),
        )
        # assemble final object (JSON string for TopController)
        final_obj = {
            "protagonist": state.get("protagonist", "Unknown"),
            "focus_aspects": state.get("focus_aspects", ["Unclear"]),
            "keypoints": out["keypoints"],
        }
        return {"keypoints": out["keypoints"], "keypoint_result": json.dumps(final_obj, ensure_ascii=False)}

    def compile(self):
        return super().compile()

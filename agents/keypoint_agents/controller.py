# agents/keypoint_agents/controller.py

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

    def extract_keypoints(self, state: dict) -> dict:
        result = self.tools.extract(state.get("input_text"))
        import json as _json
        state["keypoint_result"] = _json.dumps(result, ensure_ascii=False)
        return state

    def compile(self):
        return super().compile()

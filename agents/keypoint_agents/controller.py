# agents/keypoint_agents/controller.py
from agents.mycore.base_graph import BaseGraph
from agents.mycore.LLMclient import LLMClient

from agents.keypoint_agents.schema import KeypointAgentSchema
#from agents.keypoint_agents.tool import KeypointAgentTool


class KeypointAgent(BaseGraph):
    """Agent for extracting keypoints from text."""

    def __init__(self, llm_client: LLMClient):
        super().__init__(KeypointAgentSchema.state_type)

        # --- import schema definitions ---
        self.nodes = KeypointAgentSchema.nodes
        self.conditional_edges = KeypointAgentSchema.conditional_edges
        self.direct_edges = KeypointAgentSchema.direct_edges

        # --- load dependent graphs ---
        DEPENDENT_GRAPHS = {}
        self.subgraphs = {k: v() for k, v in DEPENDENT_GRAPHS.items()}
        self.state_mapping = KeypointAgentSchema.state_mapping
        
        # --- load tools ---
        #self.tools = KeypointAgentTool(llm_client)
    
    def extract_keypoints(self, state: dict) -> dict:
        """Extract keypoints from input text."""
        result = self.tools.extract(state.get("input_text"))
        state["keypoint_result"] = result
        return state
    
    def compile(self):
        """Compile the KeypointAgent graph using BaseGraph logic."""
        return super().compile()
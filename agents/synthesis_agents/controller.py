# agents/synthesis_agents/controller.py
import json
from agents.mycore.base_graph import BaseGraph
from agents.mycore.LLMclient import LLMClient

from agents.synthesis_agents.schema import SynthesisAgentSchema
from agents.synthesis_agents.tool import SynthesisAgentTool


class SynthesisAgent(BaseGraph):
    """Agent for synthesizing and analyzing content."""

    def __init__(self, llm_client: LLMClient):
        super().__init__(SynthesisAgentSchema.state_type)

        # --- import schema definitions ---
        self.nodes = SynthesisAgentSchema.nodes
        self.conditional_edges = SynthesisAgentSchema.conditional_edges
        self.direct_edges = SynthesisAgentSchema.direct_edges

        # --- load dependent graphs ---
        DEPENDENT_GRAPHS = {}
        self.subgraphs = {k: v() for k, v in DEPENDENT_GRAPHS.items()}
        self.state_mapping = SynthesisAgentSchema.state_mapping
        
        # --- load tools ---
        self.tools = SynthesisAgentTool(llm_client)
    
    def synthesize_content(self, state: dict) -> dict:
        result = self.tools.synthesize(state.get("input_text"))
        payload = json.dumps(result, ensure_ascii=False)
        return {"synthesis_result": payload}

    
    def compile(self):
        """Compile the SynthesisAgent graph using BaseGraph logic."""
        return super().compile()
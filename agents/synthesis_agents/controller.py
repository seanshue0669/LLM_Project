# agents/synthesis_agents/controller.py
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
        """Synthesize and analyze content from input text."""
        result = self.tools.synthesize(state.get("input_text"))
        state["synthesis_result"] = result
        return state
    
    def compile(self):
        """Compile the SynthesisAgent graph using BaseGraph logic."""
        return super().compile()
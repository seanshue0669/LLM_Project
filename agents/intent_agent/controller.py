# agents/intent_agent/controller.py
from agents.mycore.base_graph import BaseGraph
from agents.mycore.LLMclient import LLMClient

from agents.intent_agent.schema import IntentAgentSchema
from agents.intent_agent.tool import IntentAgentTool


class IntentAgent(BaseGraph):
    """Top-level orchestrator graph that coordinates subgraphs."""

    def __init__(self, llm_client: LLMClient):
        super().__init__(IntentAgentSchema.state_type)

        # --- import schema definitions ---
        self.nodes              = IntentAgentSchema.nodes
        self.conditional_edges  = IntentAgentSchema.conditional_edges
        self.direct_edges       = IntentAgentSchema.direct_edges

        # --- load dependent graphs ---
        DEPENDENT_GRAPHS={}
        self.subgraphs          = {k: v() for k, v in DEPENDENT_GRAPHS.items()}
        self.state_mapping      = IntentAgentSchema.state_mapping
        
        # --- load dependent graphs ---
        self.tools              = IntentAgentTool(llm_client)
    
    def check_input_intent(self, state: dict) -> dict:
        """Placeholder node for invoking subgraph at runtime.(Implement in controller)"""
        result = self.tools.classify(state.get("input_text"))
        state["genre_type_candidate"]   = result["genre_type"]
        state["context_type_candidate"] = result["context_type"]
        return state
    def compile(self):
        """Compile the IntentAgent graph using BaseGraph logic."""
        return super().compile()
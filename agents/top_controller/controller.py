# agents/top_controller/controller.py
from agents.mycore.base_graph import BaseGraph
from agents.mycore.LLMclient import LLMClient
from .schema import TopControllerSchema


# dependent controller
from agents.intent_agent.controller import IntentAgent
# dependent schema
from agents.intent_agent.schema import IntentAgentSchema

class TopController(BaseGraph):
    """Top-level orchestrator graph that coordinates subgraphs."""

    def __init__(self,llm_client:LLMClient):
        super().__init__(TopControllerSchema.state_type)

        # --- import schema definitions ---
        self.nodes              = TopControllerSchema.nodes
        self.conditional_edges  = TopControllerSchema.conditional_edges
        self.direct_edges       = TopControllerSchema.direct_edges

        self.subgraphs         = {}
        self.subgraph_mappings = {}

        # --- load dependent graphs and schemas ---
        DEPENDENT_GRAPHS_AND_SCHEMA = {
            "intent_agent": {
                "controller": IntentAgent,
                "schema": IntentAgentSchema
            }
        }

        for k, v in DEPENDENT_GRAPHS_AND_SCHEMA.items():
            subgraph_instance = v["controller"](llm_client)
            self.subgraphs[k] = subgraph_instance.compile()
            self.subgraph_mappings[k] = v["schema"].state_mapping

    def call_intent_agent(self, state: dict) -> dict:
        """Invoke intent agent graph with automatic state mapping."""
        
        scenario = "check_input_intent"

        # Step 1: Get the schema's state_mapping
        graphmapping = self.subgraph_mappings["intent_agent"]
        mapping = graphmapping.get(scenario)
        
        if not mapping:
            raise ValueError(f"Scenario '{scenario}' not found in intent_agent state_mapping")
        
        # Step 2: Map input: parent state -> subgraph state
        subgraph_input = self._map_input_state(state, mapping["input"])
        
        # Step 3: Invoke subgraph
        result_state = self.subgraphs["intent_agent"].invoke(subgraph_input)
        
        # Step 4: Map output: subgraph state -> parent state
        parent_update = self._map_output_state(result_state, mapping["output"])
        
        return parent_update

    def compile(self):
        """Compile the TopController graph using BaseGraph logic."""
        return super().compile()
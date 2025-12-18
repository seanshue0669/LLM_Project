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
    
    def identify_protagonist(self, state: dict) -> dict:
        out = self.tools.get_protagonist(state.get("input_text"))
        protagonist = (out.get("protagonist") or "Unknown").strip() or "Unknown"
        return {"protagonist": protagonist}
    
    def infer_focus_aspects(self, state: dict) -> dict:
        out = self.tools.get_focus_aspects(
            state.get("input_text"),
            state.get("protagonist", "Unknown")
        )

        focus_aspects = out.get("focus_aspects")
        if not isinstance(focus_aspects, list) or len(focus_aspects) == 0:
            focus_aspects = ["Unclear"]

        # Ensure all elements are strings
        focus_aspects = [str(x).strip() for x in focus_aspects if str(x).strip()]
        if not focus_aspects:
            focus_aspects = ["Unclear"]

        return {"focus_aspects": focus_aspects}
    
    def synthesize_content(self, state: dict) -> dict:
        payload = self.tools.get_synthesis_payload(
            state.get("input_text"),
            state.get("protagonist", "Unknown"),
            state.get("focus_aspects", ["Unclear"])
        )

        final_obj = {
            "protagonist": state.get("protagonist", "Unknown"),
            "focus_aspects": state.get("focus_aspects", ["Unclear"]),
            "synthesis": payload.get("synthesis", "").strip() or "Unclear input.",
            "added_context": payload.get("added_context", []) if isinstance(payload.get("added_context"), list) else [],
            "examples": payload.get("examples", []) if isinstance(payload.get("examples"), list) else [],
            "takeaways": payload.get("takeaways", []) if isinstance(payload.get("takeaways"), list) else []
        }

        synthesis_result_str = json.dumps(final_obj, ensure_ascii=False)

        return {"synthesis_result": synthesis_result_str}

    
    def compile(self):
        """Compile the SynthesisAgent graph using BaseGraph logic."""
        return super().compile()
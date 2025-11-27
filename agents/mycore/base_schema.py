# agents/mycore/base_schema.py
from typing import Optional,Callable, Dict, List, Type

class BaseSchema:
    """Base class that only describes the structure (schema) of a LangGraph graph.
    This layer holds static definitions of state, nodes, and edges, but no runtime behavior.
    """

    # --- core structural definitions ---
    state_type: Optional[Type] = None
    nodes     : List[tuple[str, Callable]] = []
    conditional_edges: List[tuple[str, Callable[[dict], str], Dict[str, str]]] = []
    direct_edges     : List[tuple[str, str]] = []

    
    def describe(self) -> Dict[str, object]:
        """Return a dictionary description of the schema structure.
        This is for inspection or debugging only.
        """
        return {
            "state_type"       : self.state_type.__name__ if self.state_type else None,
            "nodes"            : [n[0] for n in self.nodes],
            "conditional_edges": [e[0] for e in self.conditional_edges],
            "direct_edges"     : [f"{e[0]} -> {e[1]}" for e in self.direct_edges],
        }

    def validate(self) -> None:
        """Perform lightweight validation of the schema (no runtime behavior)."""
        if self.state_type is None:
            raise ValueError("Schema missing state_type definition.")
        if not self.nodes:
            raise ValueError("Schema missing node definitions.")
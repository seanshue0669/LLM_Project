# agents/mycore/base_graph.py
from langgraph.graph import StateGraph, END
from typing import Callable, Dict, List, Type


class BaseGraph:
    """Reusable base class for building LangGraph state graphs."""

    def __init__(self, state_type: Type):
        self.state_type = state_type

        # --- registries ---
        self.nodes: List[tuple[str, Callable]] = []
        self.conditional_edges: List[
            tuple[str, Callable[[dict], str], Dict[str, str]]
        ] = []
        self.direct_edges: List[tuple[str, str]] = []

        # --- graph instance placeholder ---
        self.graph = None
    # =========================================================
    # Error tracking
    # =========================================================    
    def _wrap_node(self, node_fn, node_name):
        """Wrap node function with automatic error handling"""
        def wrapped(state):
            try:
                result = node_fn(state)
                return result
            except Exception as e:
                graph_name = self.__class__.__name__
                raise Exception(f"[{graph_name}: {node_name}] {e}")
        return wrapped
    # =========================================================
    # Internal state methods (it shouldnt be overwrite)
    # =========================================================
    def _map_input_state(self, parent_state: dict, mapping: Dict[str, str]) -> dict:
        """Map parent state to subgraph state based on input mapping."""
        subgraph_state = {}
        for parent_field, subgraph_field in mapping.items():
            if parent_field in parent_state:
                subgraph_state[subgraph_field] = parent_state[parent_field]
        return subgraph_state

    def _map_output_state(self, subgraph_state: dict, mapping: Dict[str, str]) -> dict:
        """Map subgraph state to parent state based on output mapping."""
        parent_state = {}
        for subgraph_field, parent_field in mapping.items():
            if subgraph_field in subgraph_state:
                parent_state[parent_field] = subgraph_state[subgraph_field]
        return parent_state
    
    # =========================================================
    # Internal registration methods (override if needed)
    # =========================================================
    def _register_all_nodes(self):
        for node_name, fn in self.nodes:
            if hasattr(self, node_name):
                actual_fn = getattr(self, node_name)
            else:
                actual_fn = fn
            
            wrapped_fn = self._wrap_node(actual_fn ,node_name)
            
            self.graph.add_node(node_name, wrapped_fn)
    def _register_all_conditional_edges(self):
        """Register all conditional edges from the edge registry."""
        for src, route_fn, mapping in self.conditional_edges:
            self.graph.add_conditional_edges(src, route_fn, mapping)

    def _register_all_direct_edges(self):
        """Register all static (direct) edges."""
        for src, dst in self.direct_edges:
            self.graph.add_edge(src, dst)

    # =========================================================
    # Core compile method
    # =========================================================
    def compile(self):
        """Compile the full graph automatically."""
        self.graph = StateGraph(self.state_type)

        # Register components
        self._register_all_nodes()
        self._register_all_conditional_edges()
        self._register_all_direct_edges()

        # Set entry point to the first node if defined
        if self.nodes:
            self.graph.set_entry_point(self.nodes[0][0])

        # Compile and return the runnable graph
        return self.graph.compile()

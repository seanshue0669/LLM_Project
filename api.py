# api.py
from agents.top_controller.controller import TopController
from agents.mycore.LLMclient import LLMClient
from agents.mycore.error_formatter import format_error_path
class UnifyAPI:
    def __init__(self,llm_client:LLMClient):
        self.top_graph = TopController(llm_client)
        self.runnable = self.top_graph.compile()
        
    def process(self, input_text: str) -> dict:
        """
        input and return result
        
        Args:
            input_text: target context 
            
        Returns:
            dict: return as format {"success": bool, "data": dict, "error": str}
        """
        try:
            state = {
                "input_text"           : input_text,
                "selected_context_type": "",
                "selected_genre_type"  : "",
            }
            
            result = self.runnable.invoke(state)
            return {
                "success": True,
                "data": result,      
                "error": None
            }
            
        except Exception as e:
            formatted_error = format_error_path(str(e))
            return {
                "success": False,
                "data": None,
                "error": formatted_error
            }
# agents/synthesis_agents/tool.py
from agents.mycore.LLMclient import LLMClient
from agents.mycore.base_tool import BaseTool, auto_wrap_error
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

class SynthesisAgentTool(BaseTool):
    def __init__(self, client: LLMClient):
        super().__init__()
        self.client = client

    def _readjson(self, path: str) -> dict:
        """Read JSON configuration file."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read JSON file: {path}") from e
    
    @auto_wrap_error   
    def synthesize(self, text: str) -> str:
        """
        Synthesize and analyze the given text.
        
        Args:
            text: Input text to synthesize
            
        Returns:
            str: Comprehensive synthesis and analysis
        """
        system_prompt = (
            "You are a synthesis and analysis expert.\n"# Prompt unfinish yet!!!
        )
        
        user_prompt = f"Synthesize and analyze the following text:\n\n{text}"
        
        current_config = self._readjson(CONFIG_PATH)
        response = self.client.invoke(user_prompt, system_prompt, current_config) 
        
        return response["content"]
# agents/keypoint_agents/tool.py
from agents.mycore.LLMclient import LLMClient
from agents.mycore.base_tool import BaseTool, auto_wrap_error
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

class KeypointAgentTool(BaseTool):
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
    def extract(self, text: str) -> str:
        """
        Extract keypoints from the given text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            str: Extracted keypoints in structured format
        """
        system_prompt = (
            "You are a keypoint extraction expert.\n" # Prompt unfinish yet!!!
        )
        
        user_prompt = f"Extract keypoints from the following text:\n\n{text}"
        
        current_config = self._readjson(CONFIG_PATH)
        response = self.client.invoke(user_prompt, system_prompt, current_config) 
        
        return response["content"]
# agents/mycore/llm_client.py
from openai import OpenAI
from typing import Dict, Any


class LLMClient:
    """
    Minimal, stateless wrapper for OpenAI Chat Completions API.
    Handles only communication (input/output), not prompt formatting or parsing.
    """

    def __init__(self, api_key: str, default_config: Dict[str, Any]):
        """
        Initialize the LLM client.

        Args:
            api_key (str): OpenAI API key.
            default_config (dict): Default configuration shared across requests.
                                   Example:
                                   {
                                       "model": "gpt-5.1",
                                       "temperature": 0.3,
                                       "top_p": 1,
                                       "presence_penalty": 0,
                                       "frequency_penalty": 0,
                                       "response_format": {"type": "text"}
                                   }
        """
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.default_config = default_config

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """
        Update the client's default configuration dynamically.
        """
        self.default_config.update(new_config)

    def invoke(
        self,
        user_prompt:  str,
        system_prompt:str,
        config_override: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform a single chat completion call (token-in → token-out).

        Args:
            system_prompt (str): System-level instruction for the model.
            user_prompt (str): User-level input or query.
            config_override (dict | None): Optional temporary configuration
                                           to override defaults.

        Returns:
            dict: Standardized response object:
                {
                    "success": bool,
                    "content": str | None,
                    "tokens_in": int,
                    "tokens_out": int,
                    "error": str | None
                }
        """

        # Merge configs: default + override
        config = {**self.default_config, **(config_override or {})}

        # Ensure a default response_format
        if "response_format" not in config:
            config["response_format"] = {"type": "text"}

        try:
            response = self.client.chat.completions.create(
                model                   =config["model"],
                temperature             =config.get("temperature", 1),
                top_p                   =config.get("top_p", 1),
                presence_penalty        =config.get("presence_penalty", 0),
                frequency_penalty       =config.get("frequency_penalty", 0),
                max_completion_tokens   =config.get("max_tokens",500),
                response_format         =config.get("response_format"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )

            return {
                "content": response.choices[0].message.content,
                "tokens_in": response.usage.prompt_tokens,
                "tokens_out": response.usage.completion_tokens,
            }

        except Exception as e:
            raise Exception(f"[LLMClient.invoke] {e}")


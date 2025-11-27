# __init__.py
from agents.mycore.LLMclient import LLMClient
from api import UnifyAPI
from config import OPENAI_APIKEY,DEFLAUT_CONFIG

llm_client = LLMClient(
    api_key = OPENAI_APIKEY,
    default_config = DEFLAUT_CONFIG
)

app = UnifyAPI(llm_client)
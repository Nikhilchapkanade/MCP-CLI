import json
import os
from typing import List, Dict, Optional
from pydantic import BaseModel

CONFIG_FILE = "config/settings.json"

class MCPServerConfig(BaseModel):
    name: str
    command: str
    args: List[str] = []
    env: Dict[str, str] = {}

class LLMProfile(BaseModel):
    name: str
    provider: str  # "openai" or "anthropic"
    model_name: str
    api_key_env_var: str

class AppConfig(BaseModel):
    mcp_servers: List[MCPServerConfig] = []
    llm_profiles: List[LLMProfile] = []
    active_profile: Optional[str] = None
    active_server: Optional[str] = None

def load_config() -> AppConfig:
    if not os.path.exists(CONFIG_FILE):
        return AppConfig()
    with open(CONFIG_FILE, "r") as f:
        try:
            return AppConfig(**json.load(f))
        except:
            return AppConfig()

def save_config(config: AppConfig):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write(config.model_dump_json(indent=2))
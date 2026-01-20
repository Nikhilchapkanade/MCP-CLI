import os
from openai import AsyncOpenAI

class LLMClient:
    def __init__(self, provider, model_name, api_key):
        self.provider = provider
        self.model_name = model_name
        
        # Connection Logic
        base_url = None
        if provider == "openrouter":
            base_url = "https://openrouter.ai/api/v1"
        elif provider == "openai":
            base_url = "https://api.openai.com/v1"
            
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    async def chat(self, messages, tools=None):
        openai_tools = None
        if tools:
            openai_tools = [{
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            } for tool in tools]
        
        extra_headers = {}
        if self.provider == "openrouter":
            extra_headers = {
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "MCP-CLI"
            }

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=openai_tools,
            extra_headers=extra_headers
        )
        
        return response.choices[0].message
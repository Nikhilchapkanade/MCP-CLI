import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class SimpleMCPClient:
    def __init__(self, server_params: StdioServerParameters):
        self.server_params = server_params
        self.session = None
        self.exit_stack = AsyncExitStack()

    async def connect(self):
        try:
            read, write = await self.exit_stack.enter_async_context(
                stdio_client(self.server_params)
            )
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await self.session.initialize()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    async def list_tools(self):
        if not self.session: return []
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, name, arguments):
        if not self.session: raise Exception("Not connected")
        result = await self.session.call_tool(name, arguments)
        return result

    async def close(self):
        await self.exit_stack.aclose()
import asyncio
import os
import json
import sys
from contextlib import AsyncExitStack

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from dotenv import load_dotenv

# MCP Imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config_manager import load_config
from llm_handler import LLMClient

load_dotenv()
console = Console()

LOGO = r"""
[bold magenta]
  __  __  _____ ____    ____ _     ___ 
 |  \/  |/ ____|  _ \  / ___| |   |_ _|
 | |\/| | |    | |_) || |   | |    | | 
 | |  | | |____|  __/ | |___| |___ | | 
 |_|  |_|\_____|_|     \____|_____|___|
[/bold magenta]
[dim]A lightweight MCP playground for rapid testing.
[version] v0.1.4 (GitHub Ready)[/dim]
"""

async def get_input(prompt_text):
    """
    Runs the blocking Prompt.ask in a separate thread.
    """
    return await asyncio.to_thread(Prompt.ask, prompt_text)

async def run_chat_loop(session, llm):
    try:
        tools = await session.list_tools()
        console.print(f"[blue]Loaded {len(tools.tools)} tools from MCP server.[/blue]")
        tool_list = tools.tools
    except Exception as e:
        console.print(f"[red]Error listing tools: {e}[/red]")
        return

    messages = []
    
    while True:
        try:
            # Async input to prevent blocking
            user_input = await get_input("\n[bold cyan]You[/bold cyan]")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                break

            messages.append({"role": "user", "content": user_input})
            
            # 1. Get LLM Response
            with console.status("Thinking...", spinner="dots"):
                response = await llm.chat(messages, tools=tool_list)
            
            # 2. Parse Response (OpenAI/OpenRouter format)
            tool_calls = []
            final_text = ""

            if hasattr(response, 'tool_calls') and response.tool_calls:
                 tool_calls = response.tool_calls
            elif hasattr(response, 'content'):
                 final_text = str(response.content)

            if final_text:
                console.print(f"\n[bold green]Assistant[/bold green]: {final_text}")

            # 3. Handle Tools
            if tool_calls:
                messages.append(response)

                for tool_call in tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = json.loads(tool_call.function.arguments)
                    tool_id = tool_call.id

                    console.print(f"[yellow]Tool Call Requested: {fn_name}[/yellow]")
                    
                    try:
                        result = await session.call_tool(fn_name, fn_args)
                        result_text = str(result.content)
                    except Exception as e:
                        result_text = f"Error: {e}"

                    console.print(f"[dim]Result: {result_text[:100]}...[/dim]")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "content": result_text
                    })

                # 4. Final Answer
                with console.status("Synthesizing answer...", spinner="dots"):
                    final_response = await llm.chat(messages, tools=tool_list)
                    console.print(f"\n[bold green]Assistant[/bold green]: {final_response.content}")
                    messages.append(final_response)
            else:
                messages.append(response)

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[red]Loop Error: {e}[/red]")
            break

async def start_session(config):
    if not config.mcp_servers:
        console.print("[red]No servers configured![/red]")
        return

    server_cfg = config.mcp_servers[0]
    
    # Setup LLM
    profile = config.llm_profiles[0]
    api_key_var = profile.api_key_env_var
    api_key = os.getenv(api_key_var)

    if not api_key:
        console.print(f"[red]Missing {api_key_var} in .env[/red]")
        return
    
    # Initialize LLM Client
    llm = LLMClient(profile.provider, profile.model_name, api_key)

    # Setup Server Parameters - Auto-resolving paths
    command = server_cfg.command
    args = [os.path.abspath(arg) if arg.startswith("./") else arg for arg in server_cfg.args]

    server_params = StdioServerParameters(
        command=command,
        args=args,
        env={**os.environ, **server_cfg.env}
    )

    console.print(f"[green]Connecting to {server_cfg.name}...[/green]")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await run_chat_loop(session, llm)
    except Exception as e:
        console.print(f"[bold red]Connection Error:[/bold red] {e}")

async def main():
    config = load_config()
    
    while True:
        console.clear()
        console.print(LOGO)
        console.print(Panel("Available Options", title="Menu", expand=False))
        console.print("[bold]c[/bold] Chat")
        console.print("[bold]q[/bold] Quit")
        
        choice = await get_input("Choose option [c/q]: ")
        
        if choice.lower() == 'q':
            break
        elif choice.lower() == 'c':
            await start_session(config)
            await get_input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
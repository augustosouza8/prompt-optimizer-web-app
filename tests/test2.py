#!/usr/bin/env python3
"""
A CLI for interacting with an Agno Agent powered by Groq and MCPTools.
"""
import os
import asyncio

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.mcp import MCPTools, SSEClientParams

# Load environment variables
load_dotenv()

# Constants
_GROQ_API_KEY_ENV = "GROQ_API_KEY"
_SSE_URL = (
    "https://augustosouza-mcp-sentiment-server.hf.space/gradio_api/mcp/sse"
)


def get_sse_params() -> SSEClientParams:
    """
    Build and return SSEClientParams for connecting to the MCP server.
    """
    return SSEClientParams(
        url=_SSE_URL,
        headers={},            # add auth headers here if needed
        timeout=30,            # seconds to establish connection
        sse_read_timeout=300,  # seconds to wait between events
    )


def build_agent(mcp: MCPTools) -> Agent:
    """
    Construct and return an Agent configured with the Groq model and MCPTools.
    """
    model_key = os.getenv(_GROQ_API_KEY_ENV)
    if not model_key:
        raise RuntimeError(f"Environment variable '{_GROQ_API_KEY_ENV}' is not set.")

    return Agent(
        model=Groq(id="qwen/qwen3-32b"),
        tools=[mcp],
        show_tool_calls=True,  # toggle tool call visibility
        markdown=False,
        debug_mode=True,
        debug_level=2,
    )


async def run_cli_loop(agent: Agent) -> None:
    """
    Run the interactive command-line loop until user quits.
    """
    while True:
        user_input = await asyncio.to_thread(input, "\nYou: ")
        user_input = user_input.strip()
        if not user_input:
            continue
        if user_input.lower() in {"q", "quit", "exit"}:
            break

        await agent.aprint_response(user_input, stream=False)


async def main() -> None:
    """
    Entrypoint for setting up SSE connection, agent, and CLI loop.
    """
    # Ensure API key is set
    _ = os.getenv(_GROQ_API_KEY_ENV)

    # Configure MCPTools
    params = get_sse_params()

    try:
        async with MCPTools(server_params=params, transport="sse") as mcp:
            agent = build_agent(mcp)
            print("I'm an AI-powered agent specialized in telling jokes and performing sentiment analysis on phrases. "
              "If you want to exit, type 'q':")

            await run_cli_loop(agent)


    except Exception as e:
        # Suppress known SSE cleanup error on Python 3.12
        msg = str(e)
        if "generator didn't stop after athrow" in msg:
            pass
        else:
            raise


if __name__ == "__main__":
    asyncio.run(main())
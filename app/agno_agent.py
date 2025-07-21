# app/agno_agent.py

import os
import asyncio
from dotenv import load_dotenv
from builtins import BaseExceptionGroup
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.mcp import MCPTools, SSEClientParams

load_dotenv()

_GROQ_API_KEY_ENV = "GROQ_API_KEY"
# _SSE_URL = "https://augustosouza-mcp-sentiment-server.hf.space/gradio_api/mcp/sse"
_SSE_URL = "https://augustosouza-prompt-optimizer-mcp-server.hf.space/gradio_api/mcp/sse"


def get_sse_params() -> SSEClientParams:
    return SSEClientParams(
        url=_SSE_URL,
        headers={},            # add auth headers if needed
        timeout=30,            # seconds to establish connection
        sse_read_timeout=300,  # seconds between SSE events
    )


async def _query_agent_async(message: str) -> str:
    if not os.getenv(_GROQ_API_KEY_ENV):
        raise RuntimeError(f"Environment variable '{_GROQ_API_KEY_ENV}' is not set.")

    # Manually enter the SSE-based MCPTools context
    mcp = MCPTools(server_params=get_sse_params(), transport="sse")
    await mcp.__aenter__()

    try:
        # Build the agent and call its async run
        agent = Agent(
            model=Groq(id="qwen/qwen3-32b"),
            tools=[mcp],
            show_tool_calls=True,
            markdown=False,
            debug_mode=True,
            debug_level=2,
            memory=None,  # no Memory backend at all
            system_message="You are a agent that only uses the provided tools to answer the user."
                           "After running the tool call, you must only copy the tool response and sent it to the user."
                           "Do not add any extra comments. "
                           "Your final answer must be just a copy and paste from the latest tool call"
        )
        # Use the async agent method so MCPTools can drive SSE under the hood
        run_response = await agent.arun(message)

    finally:
        # Exit the context, suppressing only the Python 3.12 cancel-scope bug
        try:
            await mcp.__aexit__(None, None, None)
        except BaseExceptionGroup:
            # swallow the known TaskGroup cleanup noise
            pass
        except Exception as e:
            # any other error should bubble up
            if "cancel scope" not in str(e):
                raise

    return run_response.content


def query_agent(message: str) -> str:
    """
    Blocking entry point for Flask: runs the async helper via asyncio.run().
    """
    return asyncio.run(_query_agent_async(message))

# app/agno_agent.py

import os
import asyncio

from agno.tools.thinking import ThinkingTools
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
    mcp = MCPTools(server_params=get_sse_params(), transport="sse", timeout_seconds=30)
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
            system_message=

                "You are an agent that uses tools to answer the user. Just copy and paste the tool result to the user."

                # "You are an AI assistant with a single, critical task: execute a tool and report the result. "
                # "After the tool provides its output, you MUST return that output EXACTLY as it was given. "
                # "Your final answer must ONLY contain the raw text from the tool's response. "
                # "DO NOT add any introductory phrases, explanations, summaries, or any other text. "
                # "For example, if the tool returns 'Optimized prompt.', your response is just 'Optimized prompt.' and nothing else;"
                # "if the tool returns 'Three questions: 1. Foo? 2. Foo? 3. Foo?' your response is just '1. Foo? 2. Foo? 3. Foo?' and nothing else, ",
        )
        # Use the async agent method so MCPTools can drive SSE under the hood
        run_response = await agent.arun(message)


        ##### AUGUSTO DEBUG #####
        # print("Debug run_response await agent.arun(message).content, fetching the response by the Agno agent after receiving it from the MCP tool: ", run_response.content)
        #
        # print("Debug run_response.tools[0].result), fetching the response directly from the MCP tool: ", run_response.tools[0].result)
        #
        # if run_response.content.strip() == run_response.tools[0].result.strip():
        #     print("SAME RESPONSE")
        # else:
        #     print("DIFFERENT RESPONSE")

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

    # return run_response.content  # fetching the response by the Agno agent after receiving it from the MCP tool
    return run_response.tools[0].result.strip()  # fetching the response directly from the MCP tool


def query_agent(message: str) -> str:
    """
    Blocking entry point for Flask: runs the async helper via asyncio.run().
    """
    return asyncio.run(_query_agent_async(message))

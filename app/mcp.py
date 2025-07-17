# app/mcp.py

import asyncio
from agno.tools.mcp import MCPTools, SSEClientParams
from .agents import make_agent

# MCP SSE endpoint & discovery timeout
MCP_URL = "https://augustosouza-prompt-optimizer-mcp-server.hf.space/gradio_api/mcp/sse"
DISCOVERY_TIMEOUT = 20  # seconds

async def _optimize_via_mcp(instruction: str):
    """
    Discover MCP tools via SSE and then run the Agno agent asynchronously
    so that async MCPTools is compatible.
    """
    params = SSEClientParams(
        url=MCP_URL,
        timeout=DISCOVERY_TIMEOUT,
        sse_read_timeout=DISCOVERY_TIMEOUT
    )
    async with MCPTools(transport="sse", server_params=params) as mcp_tools:
        agent = make_agent(tools=[mcp_tools])
        # Use the async interface so MCPTools can be used
        return await agent.arun(instruction, stream=False)

def optimize_prompt(instruction: str):
    """
    Entrypoint: runs the async MCP discovery + agent.arun
    in its own event loop and returns the RunResponse.
    """
    return asyncio.run(_optimize_via_mcp(instruction))

from dotenv import load_dotenv
load_dotenv()

#!/usr/bin/env python3
import os
import asyncio

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.mcp import MCPTools, SSEClientParams

async def main():
    # 1) Ensure Groq API key is provided
    groq_key = os.getenv("GROQ_API_KEY")


    # 2) Configure SSE connection to your MCP server
    params = SSEClientParams(
        url="https://augustosouza-mcp-sentiment-server.hf.space/gradio_api/mcp/sse",
        headers={},
        timeout=30,
        sse_read_timeout=300,
    )

    try:
        # 3) Open MCPTools once
        async with MCPTools(server_params=params, transport="sse") as mcp:
            # 4) Build the Agent
            agent = Agent(
                model=Groq(id="qwen/qwen3-32b"),
                tools=[mcp],
                show_tool_calls=True,
                markdown=False,
            )

            # 5) Free‑form CLI loop
            print("Type anything (e.g. “Tell me a joke”, “Analyze sentiment of X”, or “quit” to exit):")
            while True:
                user_input = await asyncio.to_thread(input, "\nYou: ")
                if not user_input.strip():
                    continue
                if user_input.strip().lower() in {"q", "quit", "exit"}:
                    print("Goodbye!")
                    break

                # Send exactly what the user typed
                await agent.aprint_response(user_input, stream=False)

    except Exception as e:
        # Ignore the known SSE cleanup error so Python 3.12 can exit cleanly
        if "generator didn't stop after athrow" in str(e):
            print("\n⚠️  Warning: Ignored known SSE cleanup error.")
        else:
            raise

if __name__ == "__main__":
    asyncio.run(main())

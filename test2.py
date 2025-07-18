from dotenv import load_dotenv
load_dotenv()

#!/usr/bin/env python3
import os
import asyncio

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.mcp import MCPTools, SSEClientParams

async def main():
    # 1) Ensure your Groq API key is set
    groq_key = os.getenv("GROQ_API_KEY")

    # 2) Configure SSE connection to your MCP server
    params = SSEClientParams(
        url="https://augustosouza-mcp-sentiment-server.hf.space/gradio_api/mcp/sse",
        headers={},            # add auth headers here if needed
        timeout=30,            # seconds to establish connection
        sse_read_timeout=300,  # seconds to wait between events
    )

    try:
        # 3) Open MCPTools once and keep it open for the session
        async with MCPTools(server_params=params, transport="sse") as mcp:
            # 4) Build your Agent with the Groq model and MCP tools
            agent = Agent(
                model=Groq(id="qwen/qwen3-32b"),
                tools=[mcp],
                show_tool_calls=True,  # set to False if you don’t need to see each tool invocation
                markdown=False
            )

            print("Type anything and press Enter. The agent will decide whether to call your joke or sentiment tool.")
            print("Type 'quit' or 'exit' to end.\n")

            # 5) Free‑form CLI loop
            while True:
                user_input = await asyncio.to_thread(input, "You: ")
                user_input = user_input.strip()
                if not user_input:
                    continue
                if user_input.lower() in {"q", "quit", "exit"}:
                    print("Goodbye!")
                    break

                # 6) Send the user’s text to the agent and await the response
                run_response = await agent.arun(user_input)
                agent_response = run_response.content

                # 7) Now you have the agent’s reply in `agent_response`
                print("Agent:", agent_response)

    except Exception as e:
        # Suppress the known SSE cleanup error on Python 3.12 so the script exits cleanly
        if "generator didn't stop after athrow" in str(e):
            print("\n⚠️  Warning: Ignored known SSE cleanup error.")
        else:
            raise

if __name__ == "__main__":
    asyncio.run(main())
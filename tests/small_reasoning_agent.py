# REASONING AGENT


#!/usr/bin/env python3
import os
import asyncio
from dotenv import load_dotenv

# 1) Load your environment
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("Please set GROQ_API_KEY in your .env file")

# 2) Imports from Agno
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.mcp import MCPTools, SSEClientParams

async def main():
    # 3) Configure SSE connection to your MCP server
    params = SSEClientParams(
        url="https://augustosouza-mcp-sentiment-server.hf.space/gradio_api/mcp/sse",
        headers={},            # add auth headers here if needed
        timeout=30,            # seconds to establish connection
        sse_read_timeout=300,  # seconds to wait between events
    )

    try:
        # 4) Open MCPTools once and keep it open for the session
        async with MCPTools(server_params=params, transport="sse") as mcp:

            # 5) Build your Agent with full debug & reasoning
            agent = Agent(
                model=Groq(id="qwen/qwen3-32b", api_key=GROQ_API_KEY),
                # use the same Groq for reasoning
                reasoning=True,
                reasoning_model=Groq(id="qwen/qwen3-32b", api_key=GROQ_API_KEY),
                tools=[mcp],
                show_tool_calls=True,   # logs each tool in “Tool Calls” box
                markdown=False,
                debug_mode=True,
                debug_level=2,          # very verbose debug logs


                # # just also adding extra instructions   >> test the behavior without reasoning
                # instructions="Speak in spanish"


                # # use 'system_message' to set the tone of your Agent   >> test the behavior without reasoning
                # system_message="ON YOUR FINAL ANSWER YOU MUST ONLY GIVE THE USER WHAT IS ASKED"
                #                "DO NOT ADD INTRODUCTIONS TO YOUR FINAL ANSWER"
                #                "DO NOT ADD EXTRA COMMENTS OR EXPLANATIONS"
                #                "DO NOT TRY TO ENGAGE A CONVERSATION"
                #                "JUST OUTPUT WHAT YOU GOT FROM PROVIDED USED TOOL. ACT STRAIGHTFORWARD"
                #                "IF YOU SEE THAT YOU ARE BEING ASKED FOR ANYTHING DOES NO INVOLVE USING THE PROVIDED TOOLS"
                #                "JUST TELL THE USER THAT 'I'm not authorized to answer that.', DO NOT SAY ANYTHING ELSE."

            )

            print("Type anything (e.g. “Tell me a joke”, “Analyze sentiment of X”, or “quit” to exit):")

            # 6) Free‑form CLI loop
            while True:
                user_input = await asyncio.to_thread(input, "\nYou: ")
                user_input = user_input.strip()
                if not user_input:
                    continue
                if user_input.lower() in {"q", "quit", "exit"}:
                    print("Goodbye!")
                    break

                # 7) Print the full (.Message + Tool Calls + Response) output,
                #     including step‑by‑step reasoning
                await agent.aprint_response(
                    user_input,
                    stream=False,
                    show_full_reasoning=True
                )

    except Exception as e:
        # 8) Suppress known SSE cleanup errors so the script exits cleanly
        msg = str(e)
        if ("generator didn't stop after athrow" in msg
                or "exit cancel scope" in msg):
            print("\n⚠️  Warning: Ignored known SSE cleanup error.")
        else:
            # re‑raise anything else
            raise

if __name__ == "__main__":
    asyncio.run(main())

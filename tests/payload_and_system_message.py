## tracking how Agno acts under the hood: how and what it sends to the LLM to call the MCP tools

from dotenv import load_dotenv
load_dotenv()

#!/usr/bin/env python3
import os
import asyncio
import json
from typing import Optional, AsyncIterator

from agno.agent import Agent, Message
from agno.models.groq import Groq
from agno.tools.mcp import MCPTools, SSEClientParams

# ——— 1) Wrap Groq so all requests are dumped ———
class DebugGroq(Groq):
    def __init__(self, *, id: str):
        super().__init__(id=id)

    # Sync chat (non-streaming)
    def response(self, messages, **kwargs):
        payload = {
            "model": self.id,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            **kwargs
        }
        print("\n===== GROQ REQUEST PAYLOAD (sync) ===== TEST 1")
        print(json.dumps(payload, indent=2, default=lambda o: getattr(o, "__dict__", str(o))))
        print("===== END GROQ REQUEST PAYLOAD =====\n")
        return super().response(messages=messages, **kwargs)

    # Async chat (streaming)
    async def aresponse_stream(self, messages, **kwargs) -> AsyncIterator:
        payload = {
            "model": self.id,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            **kwargs
        }
        print("\n===== GROQ REQUEST PAYLOAD (async) ===== TEST 2")
        print(json.dumps(payload, indent=2, default=lambda o: getattr(o, "__dict__", str(o))))
        print("===== END GROQ REQUEST PAYLOAD =====\n")
        async for event in super().aresponse_stream(messages=messages, **kwargs):
            yield event

# ——— 2) (Optional) subclass Agent if you still want the system dump ———
class DebugAgent(Agent):
    def get_system_message(self, session_id: str, user_id: Optional[str] = None) -> Optional[Message]:
        msg = super().get_system_message(session_id, user_id)
        print("\n===== SYSTEM MESSAGE CONTENT =====")
        print(msg.content if (msg and msg.content) else "<empty>")
        print("===== end system message =====\n")
        return msg

async def main():
    # 1) GROQ key
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise RuntimeError("GROQ_API_KEY not set in environment")

    # 2) MCP SSE params
    params = SSEClientParams(
        url="https://augustosouza-mcp-sentiment-server.hf.space/gradio_api/mcp/sse",
        headers={}, timeout=30, sse_read_timeout=300
    )

    async with MCPTools(server_params=params, transport="sse") as mcp:
        # 3) Use our DebugGroq instead of the vanilla Groq
        model = DebugGroq(id="qwen/qwen3-32b")

        agent = DebugAgent(
            model=model,
            tools=[mcp],
            show_tool_calls=True,
            markdown=False,
            debug_mode=True,
            debug_level=2,
            system_message="Always write your answer in spanish",
        )

        print("Type anything (or 'quit' to exit):")
        while True:
            user_input = await asyncio.to_thread(input, "\nYou: ")
            user_input = user_input.strip()
            if not user_input:
                continue
            if user_input.lower() in {"q", "quit", "exit"}:
                print("Goodbye!")
                break

            # ——— DEBUG: show exactly what we'd send to Groq ———
            run_messages = agent.get_run_messages(
                message=user_input,
                session_id=agent.session_id or "",
                user_id=agent.user_id,
            )
            payload = {
                "model": agent.model.id,
                "messages": [{"role": m.role, "content": m.content} for m in run_messages.messages],
                "tools": agent._tools_for_model,
                "functions": agent._functions_for_model,
                "tool_choice": agent.tool_choice,
                "tool_call_limit": agent.tool_call_limit,
                "stream_model_response": False,
            }
            print("\n===== GROQ REQUEST PAYLOAD (manual debug) =====")
            print(json.dumps(payload, indent=2, default=lambda o: getattr(o, '__dict__', str(o))))
            print("===== END GROQ REQUEST PAYLOAD =====\n")

            # 4) Now invoke the agent as usual
            await agent.aprint_response(user_input, stream=False)

if __name__ == "__main__":
    asyncio.run(main())

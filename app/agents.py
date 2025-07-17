# app/agents.py

from dotenv import load_dotenv
import logging
from agno.agent import Agent
from .simple_groq import SimpleGroqModel

# Load .env for GROQ_API_KEY
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_agent(tools=None) -> Agent:
    """
    Build an Agno Agent using the flat SimpleGroqModel.
    Pass in MCPTools instances via `tools` if needed.
    """
    model = SimpleGroqModel(model_id="llama-3.1-8b-instant")
    agent = Agent(
        model=model,
        tools=tools or [],
        show_tool_calls=True,            # enable tool invocation
        add_history_to_messages=False    # avoid role/history plumbing
    )
    return agent

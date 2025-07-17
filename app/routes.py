# app/routes.py

import logging

from flask import Blueprint, render_template, request, jsonify
from mcp.shared.exceptions import McpError

from .agents import make_agent
from .mcp import optimize_prompt

main_bp = Blueprint('main', __name__)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/quick', methods=['GET', 'POST'])
def quick():
    if request.method == 'GET':
        return render_template('quick.html')

    data = request.get_json() or {}
    prompt = data.get('prompt', '').strip()
    tone = data.get('tone', '')

    # Validate inputs
    if not prompt or len(prompt) > 200:
        return jsonify(error="Prompt is required and must be ≤200 characters"), 400
    if tone not in ('Standard', 'Technical', 'Informal'):
        return jsonify(error="Invalid tone selection"), 400

    instruction = f"Rewrite the following prompt in a {tone} tone: {prompt}"

    try:
        # Try MCP-based optimization first
        run_response = optimize_prompt(instruction)
        optimized = getattr(run_response, 'content', str(run_response))
        logger.info("Quick Mode: MCP tool succeeded")

    except McpError as e:
        # Fall back to direct Groq call on MCPError (e.g. 5s timeout)
        logger.warning("MCP tool failed (%s). Falling back to direct Groq.", e)
        agent = make_agent()
        run_response = agent.run(instruction)
        optimized = getattr(run_response, 'content', str(run_response))
        logger.info("Quick Mode: direct Groq fallback succeeded")

    except Exception:
        # Any other error → user-facing fallback
        logger.exception("Unexpected error in Quick Mode")
        return jsonify(error="Sorry, please try again later."), 503

    return jsonify(enhanced=optimized), 200

@main_bp.route('/interactive')
def interactive():
    return render_template('interactive.html')

import os
import asyncio
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from .agno_agent   import query_agent

proxy_bp = Blueprint('proxy', __name__)

@proxy_bp.route('/optimize', methods=['POST'])
@cross_origin()  # allow your Chrome extension to call it
def optimize():
    """
    Expects JSON: { "prompt": "<original user prompt>" }
    Returns JSON: { "optimized_prompt": "<agent's reply>" }
    """
    payload = request.get_json(force=True, silent=True)
    if not payload or "prompt" not in payload:
        return jsonify({"error": "Missing 'prompt' field"}), 400

    original = payload["prompt"]
    try:
        optimized = query_agent("Call the prompt_optimizer_mcp_server_one_shot_optimization tool to optimize the following initial prompt:", original)
        return jsonify({"optimized_prompt": optimized})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
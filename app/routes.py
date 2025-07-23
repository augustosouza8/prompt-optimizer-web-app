from flask import Blueprint, render_template, request, session
from .agno_agent import query_agent
import re

main_bp = Blueprint('main', __name__)

# ────────────────────────────────────────────────────────────────────────────────
# Define the five interactive questions in one place:
INTERACTIVE_QUESTIONS = [
    "What is your goal or what do you want to achieve?",
    "What specific information or input do you have?",
    "What format or output style do you prefer?",
    "Who is the target audience, if any?",
    "Are there any constraints or things to avoid/include?"
]
# ────────────────────────────────────────────────────────────────────────────────

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/quick', methods=['GET', 'POST'])
def quick():
    user_input = None
    prompt_styling = None
    response = None

    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        prompt_styling = request.form.get('tone', '').strip()
        if user_input:
            try:
                response = query_agent(f"Call the prompt_optimizer_mcp_server_one_shot_optimization tool to optimize the following initial prompt idea and writing tone: '{user_input} [Please consider a {prompt_styling} writing tone to optimize the given prompt]'")
            except Exception as e:
                response = f"Error: {e}"

    return render_template('quick.html', user_input=user_input, response=response)

@main_bp.route('/interactive', methods=['GET'])
def interactive():
    # Pass the questions into the template instead of hard‑coding
    return render_template('interactive_step1.html', questions=INTERACTIVE_QUESTIONS)

@main_bp.route('/interactive', methods=['POST'])
def interactive_submit():
    # 1) Re‑use the same list of questions here
    questions = INTERACTIVE_QUESTIONS
    answers = [request.form.get(f"q{i}", "").strip() for i in range(1, 6)]
    qas = [{"q": questions[i], "a": answers[i]} for i in range(5)]

    # 2) Persist them in session
    session['interactive_qas'] = qas

    # 3) Build and send the tool call to MCP
    prompt_lines = ["Call the prompt_optimizer_mcp_server_five_questions_analysis_and_followup_generation tool to analyse the given 5 questions and answers and generate 3 follow-up questions:"]
    for pair in qas:
        prompt_lines.append(f"Question: {pair['q']}\nAnswer: {pair['a']}")
    prompt = "\n\n".join(prompt_lines)

    raw_followups = query_agent(prompt)

    # 4) Parse out exactly three follow‑up questions
    followups = parse_numbered_list(raw_followups, count=3)

    # 5) Show step 2
    return render_template('interactive_step2.html', followups=followups)

@main_bp.route('/interactive/followup', methods=['POST'])
def interactive_followup():
    # 1) Retrieve the original Q&A from session
    qas = session.get('interactive_qas', [])

    # 2) Collect the three follow‑up Q&A
    follow_qs = request.form.getlist('follow_q')
    follow_as = request.form.getlist('follow_a')
    followups = [{"q": follow_qs[i], "a": follow_as[i]} for i in range(len(follow_qs))]

    # 3) Build and send the final tool call
    prompt_lines = ["Call the prompt_optimizer_mcp_server_eight_questions_analysis_and_prompt_generation tool to analyse the 8 given questions and generate a final prompt:"]
    for pair in qas + followups:
        prompt_lines.append(f"Question: {pair['q']}\nAnswer: {pair['a']}")
    prompt = "\n\n".join(prompt_lines)

    analysis = query_agent(prompt)

    # 4) Render the final analysis to the user
    return render_template('interactive_result.html', analysis=analysis)

# — Helper to extract numbered list items from free text —
def parse_numbered_list(text, count):
    """
    Finds lines like "1. Foo?" and returns ["Foo?", ...] up to `count` items.
    """
    pattern = r'^\s*\d+\.\s*(.+)$'
    lines = re.findall(pattern, text, flags=re.MULTILINE)
    return lines[:count]

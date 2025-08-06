from flask import Blueprint, render_template, request, session
from .agno_agent import query_agent
import re

main_bp = Blueprint('main', __name__)

# ────────────────────────────────────────────────────────────────────────────────
# Define the five interactive questions in one place:
INTERACTIVE_QUESTIONS = [
    "1. What problem or challenge in your life is driving you to seek help from an Artificial Intelligence like ChatGPT right now?",
    "2. What role or expertise should the Artificial Intelligence adopt when responding to you (e.g., expert consultant, creative partner, technical analyst, history teacher)?",
    "3. What format or style do you want the response to be in (e.g., formal report, casual explanation, step-by-step guide, creative content)?",
    "4. Are there any specific constraints, limitations, or anything in particular that should be focused on?",
    "5. Would you like to add anything else about your demand?"
]
# ────────────────────────────────────────────────────────────────────────────────

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/quick', methods=['GET', 'POST'])
def quick():
    user_input     = None
    raw_tone       = 'Standard'
    custom_tone    = ''
    prompt_styling = None
    response       = None

    if request.method == 'POST':
        # grab what the user typed and their tone selection
        user_input  = request.form.get('user_input', '').strip()
        raw_tone    = request.form.get('tone', 'Standard')
        custom_tone = request.form.get('custom_tone', '').strip()

        # decide what to actually send to the agent
        if raw_tone == 'Custom':
            prompt_styling = custom_tone or 'Standard'
        else:
            prompt_styling = raw_tone

        if user_input:
            try:
                response = query_agent(
                    f"Call the prompt_optimizer_mcp_server_one_shot_optimization "
                    f"tool to optimize the following initial prompt idea and writing tone: "
                    f"'{user_input} [Please consider a {prompt_styling} writing tone to optimize the given prompt]'"
                )
            except Exception as e:
                response = f"Error: {e}"

    return render_template(
        'quick.html',
        user_input=user_input,
        response=response,
        selected_tone=raw_tone,
        custom_tone=custom_tone,
        prompt_styling=prompt_styling
    )


@main_bp.route('/interactive', methods=['GET'])
def interactive():
    return render_template('interactive_step1.html', questions=INTERACTIVE_QUESTIONS)


@main_bp.route('/interactive', methods=['POST'])
def interactive_submit():
    questions = INTERACTIVE_QUESTIONS
    answers   = [request.form.get(f"q{i}", "").strip() for i in range(1, 6)]
    qas       = [{"q": questions[i], "a": answers[i]} for i in range(5)]

    session['interactive_qas'] = qas

    prompt_lines = [
        "Call the tool named prompt_optimizer_mcp_server_five_questions_analysis_and_followup_generation "
        "to analyse the following 5 questions and answers and generate 3 follow-up questions:"
    ]
    for pair in qas:
        prompt_lines.append(f"Question: {pair['q']}\nAnswer: {pair['a']}")

    raw_followups = query_agent("\n\n".join(prompt_lines))
    followups     = parse_numbered_list(raw_followups, count=3)

    return render_template('interactive_step2.html', followups=followups)


@main_bp.route('/interactive/followup', methods=['POST'])
def interactive_followup():
    qas = session.get('interactive_qas', [])

    follow_qs = request.form.getlist('follow_q')
    follow_as = request.form.getlist('follow_a')
    followups = [{"q": follow_qs[i], "a": follow_as[i]} for i in range(len(follow_qs))]

    prompt_lines = [
        "Call the tool named prompt_optimizer_mcp_server_eight_questions_analysis_and_prompt_generation "
        "to analyse the 8 given questions and generate a final prompt:"
    ]
    for pair in qas + followups:
        prompt_lines.append(f"Question: {pair['q']}\nAnswer: {pair['a']}")

    analysis = query_agent("\n\n".join(prompt_lines))
    return render_template('interactive_result.html', analysis=analysis)


def parse_numbered_list(text, count):
    """
    Finds lines like "1. Foo?" and returns ["Foo?", ...] up to `count` items.
    """
    pattern = r'^\s*\d+\.\s*(.+)$'
    lines   = re.findall(pattern, text, flags=re.MULTILINE)
    return lines[:count]

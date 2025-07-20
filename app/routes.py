from flask import Blueprint, render_template, request
from .agno_agent import query_agent

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/quick', methods=['GET', 'POST'])
def quick():
    user_input = None
    response = None

    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        # user_input = (f"Optimize the following prompt: {user_input}")
        print("That's the user_input:", user_input)
        if user_input:
            try:
                response = query_agent(f"Optimize the following prompt: {user_input}")
            except Exception as e:
                response = f"Error: {e}"

    return render_template('quick.html',
                           user_input=user_input,
                           response=response)

@main_bp.route('/interactive')
def interactive():
    return render_template('interactive.html')

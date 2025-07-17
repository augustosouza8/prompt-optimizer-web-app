from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/quick')
def quick():
    return render_template('quick.html')

@main_bp.route('/interactive')
def interactive():
    return render_template('interactive.html')
# app/__init__.py
import os
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # or just around your proxy routes

    app.secret_key = os.getenv('SECRET_KEY', 'dev_secret_key')

    # web UI
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # proxy for Chrome extension
    from .proxy import proxy_bp
    app.register_blueprint(proxy_bp)

    return app


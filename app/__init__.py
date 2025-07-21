# app/__init__.py

import os
from flask import Flask

def create_app():
    app = Flask(__name__)

    # ——— SECRET KEY (required for session) ———
    # In production, set the SECRET_KEY env var; here we default to a dev key.
    app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')

    # Register routes
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app

"""
moodblume/__init__.py
Application factory — creates and configures the Flask app.
"""
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from .context import register_context_processors
from .routes.auth import auth_bp
from .routes.main import main_bp
from .routes.journal import journal_bp
from .routes.collections import collections_bp
from .routes.profile import profile_bp, register_error_handlers


def create_app():
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static',
    )
    app.secret_key = 'super_secret_moodblume_key'
    app.debug = True

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(collections_bp)
    app.register_blueprint(profile_bp)

    # ── Context processors ────────────────────────────────────────────────────
    register_context_processors(app)

    # ── Error handlers ────────────────────────────────────────────────────────
    register_error_handlers(app)

    return app

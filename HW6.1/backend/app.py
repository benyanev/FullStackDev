"""Flask REST API for SocialApp — application entry point.

Uses the Application Factory pattern:  ``create_app()`` builds and
configures the Flask instance, initialises extensions, and registers
all route blueprints.  Running this file directly starts the dev server.
"""

from flask import Flask

from core.config import SECRET_KEY
from core.extensions import cors, limiter
from repositories.session_repository import delete_expired_sessions
from routes.auth_routes import auth_bp
from routes.follow_routes import follow_bp
from routes.post_routes import post_bp
from routes.upload_routes import upload_bp
from routes.user_routes import user_bp


def create_app():
    """Application factory — create and configure the Flask app."""
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Initialise extensions (created in core/extensions.py)
    cors.init_app(
        app, origins=['http://localhost:5173'], supports_credentials=True)
    limiter.init_app(app)

    # Register route blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(follow_bp)
    app.register_blueprint(upload_bp)

    return app


if __name__ == '__main__':
    # Clean up expired sessions on startup
    deleted = delete_expired_sessions()
    if deleted:
        print(f'Cleaned up {deleted} expired session(s).')

    app = create_app()
    app.run(debug=True, port=5000)

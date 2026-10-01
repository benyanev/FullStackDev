"""Flask REST API for SocialApp — application entry point.

Uses the Application Factory pattern:  ``create_app()`` builds and
configures the Flask instance, initialises extensions, and registers
all route blueprints.  Running this file directly starts the dev server.
"""

import os

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from core.config import (
    BEHIND_PROXY,
    CORS_ORIGINS,
    MAX_CONTENT_LENGTH,
    PROXY_HOPS,
    RATELIMIT_ENABLED,
    SECRET_KEY,
)
from core.extensions import cors, limiter
from repositories.session_repository import delete_expired_sessions
from routes.admin_routes import admin_bp
from routes.ai_routes import ai_bp
from routes.auth_routes import auth_bp
from routes.comment_routes import comment_bp
from routes.follow_routes import follow_bp
from routes.like_routes import like_bp
from routes.post_routes import post_bp
from routes.report_routes import report_bp
from routes.reset_routes import reset_bp
from routes.upload_routes import upload_bp
from routes.user_routes import user_bp


def create_app():
    """Application factory — create and configure the Flask app."""
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    # Reject oversized uploads (413) before Flask reads them into memory
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

    # Behind nginx (and Caddy on AWS): trust exactly PROXY_HOPS proxies for
    # the client IP and the http/https scheme
    if BEHIND_PROXY:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=PROXY_HOPS, x_proto=PROXY_HOPS)

    # Initialise extensions (created in core/extensions.py)
    cors.init_app(app, origins=CORS_ORIGINS, supports_credentials=True)
    app.config['RATELIMIT_ENABLED'] = RATELIMIT_ENABLED
    limiter.init_app(app)

    # Register route blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(follow_bp)
    app.register_blueprint(like_bp)
    app.register_blueprint(reset_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)

    # Errors are always JSON (never Flask's HTML pages), so the frontend
    # can show the message instead of failing to parse the response.
    @app.errorhandler(413)
    def request_too_large(_error):
        return jsonify({'error': 'File too large. Maximum size is 50 MB.'}), 413

    @app.errorhandler(HTTPException)
    def http_error(error):
        # 404 unknown URL, 405 wrong method, 429 rate limit, ...
        return jsonify({'error': error.description}), error.code

    @app.errorhandler(Exception)
    def unexpected_error(error):
        # Full details go to the server log only, never to the client
        app.logger.exception('Unhandled error: %s', error)
        return jsonify({'error': 'Something went wrong. Please try again.'}), 500

    return app


if __name__ == '__main__':
    # Clean up expired sessions on startup
    deleted = delete_expired_sessions()
    if deleted:
        print(f'Cleaned up {deleted} expired session(s).')

    app = create_app()
    # Debug mode (auto-reload + interactive debugger) only for local development
    app.run(debug=os.environ.get('FLASK_DEBUG', '1') == '1', port=5000)

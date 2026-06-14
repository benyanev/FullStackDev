"""Auth routes — URL-to-controller mapping for authentication endpoints.

This module only declares endpoints and applies rate limiting / auth
decorators.  All logic lives in :mod:`controllers.auth_controller`.
"""

from flask import Blueprint

from controllers import auth_controller
from core.extensions import limiter
from middlewares.auth_middleware import auth_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/signup', methods=['POST'])
@limiter.limit('5 per minute')
def signup():
    """Register a new user. Sets a session cookie on success."""
    return auth_controller.signup()


@auth_bp.route('/api/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    """Authenticate a user. Sets a session cookie on success."""
    return auth_controller.login()


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """Log out the current user by destroying the session."""
    return auth_controller.logout()


@auth_bp.route('/api/me', methods=['GET'])
@auth_required
def get_current_user():
    """Return the currently authenticated user's info."""
    return auth_controller.get_current_user()

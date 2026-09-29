"""Authentication middleware — session cookie management and auth decorator.

Provides the ``auth_required`` / ``admin_required`` decorators used by
protected routes and helper functions for setting/clearing session
cookies on responses.
"""

from datetime import datetime, timezone
from functools import wraps

from flask import jsonify, request

from core.config import IS_PRODUCTION, SESSION_MAX_AGE
from repositories.session_repository import delete_session, get_session
from repositories.user_repository import get_user_by_id


# ---------------------------------------------------------------------------
# Session / Cookie Helpers
# ---------------------------------------------------------------------------

def set_session_cookie(response, session_id):
    """Attach the session cookie to a Flask response.

    Cookie settings for security:
    - httponly: prevents JavaScript access (XSS protection)
    - secure: only sent over HTTPS in production (disabled in dev)
    - samesite: 'Lax' allows safe cross-origin requests during navigation
    - max_age: matches the server-side session TTL
    - path: '/' ensures the cookie is sent on every request
    """
    response.set_cookie(
        'session_id',
        session_id,
        httponly=True,
        secure=IS_PRODUCTION,
        samesite='Lax',
        max_age=SESSION_MAX_AGE,
        path='/',
    )


def clear_session_cookie(response):
    """Remove the session cookie from the browser."""
    response.set_cookie(
        'session_id',
        '',
        httponly=True,
        secure=IS_PRODUCTION,
        samesite='Lax',
        max_age=0,
        path='/',
    )


# ---------------------------------------------------------------------------
# Auth Decorator
# ---------------------------------------------------------------------------

def _check_session():
    """Validate the 'session_id' cookie against the sessions table.

    Returns:
        ``(user_id, None)`` for a valid session, or
        ``(None, (json_response, status))`` explaining why it is not valid.
    """
    session_id = request.cookies.get('session_id')
    if not session_id:
        return None, (jsonify({'error': 'Authentication required.'}), 401)

    session = get_session(session_id)
    if session is None:
        return None, (jsonify({'error': 'Invalid session.'}), 401)

    # Check if the session has expired (DB times are UTC)
    expires_at = session['expires_at']
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        # Clean up the expired session from the database
        delete_session(session_id)
        return None, (jsonify({'error': 'Session expired. Please log in again.'}), 401)

    # A user banned while logged in is stopped on their very next request
    if session.get('is_banned'):
        delete_session(session_id)
        return None, (jsonify({'error': 'This account has been banned.'}), 403)

    return session['user_id'], None


def auth_required(f):
    """Decorator that requires a valid session cookie.

    Validates the session (exists, not expired, user not banned) and
    attaches request.user_id for the route handler.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id, error = _check_session()
        if error:
            return error

        # Attach user_id to the request for use in the route
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated


def get_optional_user_id():
    """Return the logged-in user's ID, or None for visitors.

    For public endpoints that show extra info to logged-in users
    (e.g. whether *you* liked a post).
    """
    if not request.cookies.get('session_id'):
        return None
    user_id, _ = _check_session()
    return user_id


def admin_required(f):
    """Decorator that requires a valid session AND the 'admin' role.

    Runs ``auth_required`` first (401 if not logged in), then loads the
    user and returns 403 unless they are an admin.
    """
    @wraps(f)
    @auth_required
    def decorated(*args, **kwargs):
        user = get_user_by_id(request.user_id)
        if user is None or user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required.'}), 403
        return f(*args, **kwargs)
    return decorated

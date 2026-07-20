"""Authentication middleware — session cookie management and auth decorator.

Provides the ``auth_required`` decorator used by protected routes and
helper functions for setting/clearing session cookies on responses.
"""

from datetime import datetime, timezone
from functools import wraps

from flask import jsonify, request

from core.config import IS_PRODUCTION, SESSION_MAX_AGE
from repositories.session_repository import delete_session, get_session


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

def auth_required(f):
    """Decorator that requires a valid session cookie.

    Reads the 'session_id' cookie, validates it against the sessions table,
    checks expiry, and attaches request.user_id for the route handler.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        session_id = request.cookies.get('session_id')
        if not session_id:
            return jsonify({'error': 'Authentication required.'}), 401

        session = get_session(session_id)
        if session is None:
            return jsonify({'error': 'Invalid session.'}), 401

        # Check if the session has expired
        expires_at = session['expires_at']
        # Ensure timezone-aware comparison
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            # Clean up the expired session from the database
            delete_session(session_id)
            return jsonify({'error': 'Session expired. Please log in again.'}), 401

        # Attach user_id to the request for use in the route
        request.user_id = session['user_id']
        return f(*args, **kwargs)
    return decorated

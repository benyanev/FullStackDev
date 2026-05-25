"""Flask REST API for SocialApp — authentication, posts, and users endpoints."""

import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

import bcrypt
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from db import (
    create_post,
    create_session,
    create_user,
    delete_expired_sessions,
    delete_session,
    delete_user_sessions,
    get_posts_paginated,
    get_session,
    get_user_by_email,
    get_user_by_id,
    get_users_paginated,
)

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# Session lifetime in seconds (24 hours)
SESSION_MAX_AGE = 24 * 60 * 60

app = Flask(__name__)

# Allow React dev server with credentials (cookies)
CORS(app, origins=['http://localhost:5173'], supports_credentials=True)

# Secret key for Flask (required best practice, even with custom sessions)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(32))

# Detect production vs development for cookie security settings
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'

# Rate limiter to protect auth endpoints from brute-force attacks
limiter = Limiter(get_remote_address, app=app, default_limits=[])


# ---------------------------------------------------------------------------
# Session / Cookie Helpers
# ---------------------------------------------------------------------------

def _set_session_cookie(response, session_id):
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


def _clear_session_cookie(response):
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


def _create_session_for_user(user_id):
    """Create a DB session and return the session ID string."""
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=SESSION_MAX_AGE)
    return create_session(user_id, expires_at)


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


# ---------------------------------------------------------------------------
# Auth Routes
# ---------------------------------------------------------------------------

@app.route('/api/signup', methods=['POST'])
@limiter.limit('5 per minute')
def signup():
    """Register a new user. Sets a session cookie on success."""
    data = request.get_json()
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    # Validation
    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required.'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400

    # Check if email already exists
    if get_user_by_email(email) is not None:
        return jsonify({'error': 'An account with this email already exists.'}), 409

    # Hash password with bcrypt
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Save to database
    user_id = create_user(name, email, password_hash.decode('utf-8'))

    # Create server-side session and set cookie
    session_id = _create_session_for_user(user_id)
    response = make_response(jsonify({
        'user': {'id': user_id, 'name': name, 'email': email},
    }), 201)
    _set_session_cookie(response, session_id)
    return response


@app.route('/api/login', methods=['POST'])
@limiter.limit('10 per minute')
def login():
    """Authenticate a user. Sets a session cookie on success.

    Invalidates all existing sessions for the user before creating
    a new one to enforce single-session policy.
    """
    data = request.get_json()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    # Look up user
    user = get_user_by_email(email)
    if user is None:
        return jsonify({'error': 'Invalid email or password.'}), 401

    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'error': 'Invalid email or password.'}), 401

    # Invalidate any existing sessions for this user (single-session enforcement)
    delete_user_sessions(user['id'])

    # Create server-side session and set cookie
    session_id = _create_session_for_user(user['id'])
    response = make_response(jsonify({
        'user': {'id': user['id'], 'name': user['name'], 'email': user['email']},
    }))
    _set_session_cookie(response, session_id)
    return response


@app.route('/api/logout', methods=['POST'])
def logout():
    """Log out the current user by destroying the session."""
    session_id = request.cookies.get('session_id')
    if session_id:
        delete_session(session_id)

    response = make_response(jsonify({'message': 'Logged out.'}))
    _clear_session_cookie(response)
    return response


@app.route('/api/me', methods=['GET'])
@auth_required
def get_current_user():
    """Return the currently authenticated user's info.

    Used by the frontend on page load to restore the session
    without needing localStorage.
    """
    user = get_user_by_id(request.user_id)
    if user is None:
        return jsonify({'error': 'User not found.'}), 404

    if isinstance(user.get('created_at'), datetime):
        user['created_at'] = user['created_at'].isoformat()

    return jsonify({'user': user})


# ---------------------------------------------------------------------------
# Posts Routes
# ---------------------------------------------------------------------------

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Get paginated posts. Query params:
    - _start (default 0): pagination offset
    - _limit (default 10): number of posts
    - userId (optional): filter by user ID
    """
    start = request.args.get('_start', 0, type=int)
    limit = request.args.get('_limit', 10, type=int)
    user_id = request.args.get('userId', None, type=int)

    posts = get_posts_paginated(start, limit, user_id)

    # Convert datetime objects to ISO strings for JSON serialization
    for post in posts:
        if isinstance(post.get('created_at'), datetime):
            post['created_at'] = post['created_at'].isoformat()

    return jsonify(posts)


@app.route('/api/posts', methods=['POST'])
@auth_required
def create_new_post():
    """Create a new post. Requires authentication (session cookie)."""
    data = request.get_json()
    title = (data.get('title') or '').strip()
    body = (data.get('body') or '').strip()

    if not title or not body:
        return jsonify({'error': 'Title and body are required.'}), 400

    post_id = create_post(request.user_id, title, body)
    return jsonify({'id': post_id, 'message': 'Post created successfully.'}), 201


# ---------------------------------------------------------------------------
# Users Routes
# ---------------------------------------------------------------------------

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get paginated users.

    Query params:
    - _start (default 0): pagination offset
    - _limit (default 100): number of users
    """
    start = request.args.get('_start', 0, type=int)
    limit = request.args.get('_limit', 100, type=int)

    users = get_users_paginated(start, limit)

    # Convert datetime objects for JSON serialization
    for user in users:
        if isinstance(user.get('created_at'), datetime):
            user['created_at'] = user['created_at'].isoformat()

    return jsonify(users)


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get a single user by ID."""
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({'error': 'User not found.'}), 404

    if isinstance(user.get('created_at'), datetime):
        user['created_at'] = user['created_at'].isoformat()

    return jsonify(user)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    # Clean up expired sessions on startup
    deleted = delete_expired_sessions()
    if deleted:
        print(f'Cleaned up {deleted} expired session(s).')

    app.run(debug=True, port=5000)

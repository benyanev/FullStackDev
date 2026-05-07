"""Flask REST API for SocialApp — authentication, posts, and users endpoints."""

import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

import bcrypt
import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from db import (
    create_post,
    create_user,
    get_posts_paginated,
    get_user_by_email,
    get_user_by_id,
    get_users_paginated,
)

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

JWT_SECRET = os.environ.get('JWT_SECRET', 'fallback-secret')

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173'])  # Allow React dev server only


# ---------------------------------------------------------------------------
# JWT Helpers
# ---------------------------------------------------------------------------

def generate_token(user_id):
    """Create a JWT token that expires in 24 hours."""
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def decode_token(token):
    """Decode and verify a JWT token. Returns the payload or None."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def auth_required(f):
    """Decorator that requires a valid JWT in the Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token.'}), 401

        token = auth_header.split(' ')[1]
        payload = decode_token(token)
        if payload is None:
            return jsonify({'error': 'Invalid or expired token.'}), 401

        # Attach user_id to the request for use in the route
        request.user_id = payload['user_id']
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Auth Routes
# ---------------------------------------------------------------------------

@app.route('/api/signup', methods=['POST'])
def signup():
    """Register a new user. Returns a JWT token on success."""
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

    # Return JWT token + user info
    token = generate_token(user_id)
    return jsonify({
        'token': token,
        'user': {'id': user_id, 'name': name, 'email': email},
    }), 201


@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate a user. Returns a JWT token on success."""
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

    # Return JWT token + user info
    token = generate_token(user['id'])
    return jsonify({
        'token': token,
        'user': {'id': user['id'], 'name': user['name'], 'email': user['email']},
    })


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
    """Create a new post. Requires authentication (JWT)."""
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
    app.run(debug=True, port=5000)

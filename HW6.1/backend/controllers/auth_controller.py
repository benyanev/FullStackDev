"""Auth controller — HTTP layer for authentication endpoints.

Parses Flask request data, delegates to :mod:`services.auth_service`,
catches service exceptions, and formats JSON responses with appropriate
status codes.  Session cookies are set/cleared here because they are
an HTTP concern.
"""

from flask import jsonify, make_response, request

from core.exceptions import AppError
from middlewares.auth_middleware import clear_session_cookie, set_session_cookie
from services import auth_service
from utils.serializers import serialize_dates


def signup():
    """Handle ``POST /api/signup``."""
    data = request.get_json()
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    try:
        user, session_id = auth_service.signup(name, email, password)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    response = make_response(jsonify({'user': user}), 201)
    set_session_cookie(response, session_id)
    return response


def login():
    """Handle ``POST /api/login``."""
    data = request.get_json()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    try:
        user, session_id = auth_service.login(email, password)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    response = make_response(jsonify({'user': user}))
    set_session_cookie(response, session_id)
    return response


def logout():
    """Handle ``POST /api/logout``."""
    session_id = request.cookies.get('session_id')
    auth_service.logout(session_id)

    response = make_response(jsonify({'message': 'Logged out.'}))
    clear_session_cookie(response)
    return response


def get_current_user():
    """Handle ``GET /api/me``."""
    try:
        user = auth_service.get_current_user(request.user_id)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    serialize_dates(user, 'created_at')
    return jsonify({'user': user})

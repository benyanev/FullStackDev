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
from utils.request_helpers import get_text, json_body
from utils.serializers import serialize_dates


def signup():
    """Handle ``POST /api/signup``."""
    data = json_body()
    name = get_text(data, 'name')
    email = get_text(data, 'email').lower()
    password = data.get('password') if isinstance(data.get('password'), str) else ''

    try:
        user, session_id = auth_service.signup(name, email, password)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    response = make_response(jsonify({'user': user}), 201)
    set_session_cookie(response, session_id)
    return response


def login():
    """Handle ``POST /api/login``."""
    data = json_body()
    email = get_text(data, 'email').lower()
    password = data.get('password') if isinstance(data.get('password'), str) else ''

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

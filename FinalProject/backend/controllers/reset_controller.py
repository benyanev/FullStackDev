"""Reset controller — HTTP layer for password reset endpoints.

Parses JSON bodies, delegates to :mod:`services.reset_service`,
and returns JSON responses.
"""

from flask import jsonify

from core.exceptions import AppError
from services import reset_service
from utils.request_helpers import get_text, json_body


def request_reset():
    """Handle ``POST /api/reset-request``.

    Expects JSON body: ``{"email": "user@example.com"}``.
    Always returns 200 to prevent user enumeration.
    """
    email = get_text(json_body(), 'email').lower()

    try:
        reset_service.request_reset(email)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({
        'message': 'If an account with that email exists, a reset link has been sent.',
    })


def confirm_reset():
    """Handle ``POST /api/reset-confirm``.

    Expects JSON body: ``{"token": "...", "password": "newpass"}``.
    """
    data = json_body()
    token = get_text(data, 'token')
    # Not stripped: spaces are part of the password (same as signup/login)
    password = data.get('password') if isinstance(data.get('password'), str) else ''

    try:
        reset_service.confirm_reset(token, password)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'message': 'Password has been reset successfully.'})

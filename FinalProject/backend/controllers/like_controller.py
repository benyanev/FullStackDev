"""Like controller — HTTP layer for like endpoints.

Parses path parameters, delegates to :mod:`services.like_service`,
and returns JSON responses.
"""

from flask import jsonify, request

from core.exceptions import AppError
from middlewares.auth_middleware import get_optional_user_id
from services import like_service


def toggle_like(post_id):
    """Handle ``POST /api/posts/<id>/like``."""
    try:
        result = like_service.toggle_like(request.user_id, post_id)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify(result)


def get_post_likes(post_id):
    """Handle ``GET /api/posts/<id>/likes``."""
    # Public route: logged-in users also get their own "liked" state
    user_id = get_optional_user_id()

    try:
        result = like_service.get_post_likes(user_id, post_id)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify(result)

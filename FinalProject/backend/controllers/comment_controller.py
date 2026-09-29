"""Comment controller — HTTP layer for comment endpoints.

Parses JSON bodies and path parameters, delegates to
:mod:`services.comment_service`, and serializes datetime fields.
"""

from flask import jsonify, request

from core.exceptions import AppError
from services import comment_service
from utils.request_helpers import get_text, json_body
from utils.serializers import serialize_dates_list


def create_comment(post_id):
    """Handle ``POST /api/posts/<id>/comments``."""
    # Comments are flat (the UI has no replies), so parent_id is not accepted
    body = get_text(json_body(), 'body')

    try:
        comment_id = comment_service.add_comment(post_id, request.user_id, body)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({
        'id': comment_id,
        'message': 'Comment created successfully.',
    }), 201


def get_comments(post_id):
    """Handle ``GET /api/posts/<id>/comments``."""
    try:
        result = comment_service.get_comments(post_id)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    serialize_dates_list(result['comments'], 'created_at')
    return jsonify(result)

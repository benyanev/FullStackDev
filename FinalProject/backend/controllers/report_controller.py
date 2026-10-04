"""Report controller — HTTP layer for reporting posts.

Parses the JSON body, delegates to :mod:`services.report_service`,
and returns JSON responses.
"""

from flask import jsonify, request

from core.exceptions import AppError
from services import report_service
from utils.request_helpers import get_text, json_body


def create_report():
    """Handle ``POST /api/reports``.

    Expects JSON body: ``{"post_id": 1, "reason": "Spam"}``.
    """
    data = json_body()
    post_id = data.get('post_id')
    reason = get_text(data, 'reason')

    if not isinstance(post_id, int):
        return jsonify({'error': 'post_id is required.'}), 400

    try:
        report_service.create_report(request.user_id, post_id, reason)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'message': 'Thanks — a moderator will review this post.'}), 201

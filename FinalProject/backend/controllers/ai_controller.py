"""AI controller — HTTP layer for the AI Assist endpoints.

Parses JSON bodies, delegates to :mod:`services.ai_service`, and returns
JSON responses.
"""

from flask import jsonify

from core.exceptions import AppError
from services import ai_service
from utils.request_helpers import get_text, json_body


def autocorrect():
    """Handle ``POST /api/ai/autocorrect`` — body ``{"text": "..."}``."""
    try:
        text = ai_service.autocorrect(get_text(json_body(), 'text'))
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'text': text})


def suggest_post():
    """Handle ``POST /api/ai/suggest-post`` — body ``{"topic": "..."}``."""
    try:
        post = ai_service.suggest_post(get_text(json_body(), 'topic'))
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify(post)


def suggest_comment():
    """Handle ``POST /api/ai/suggest-comment`` — body ``{"post_id": 1}``."""
    post_id = json_body().get('post_id')

    if not isinstance(post_id, int):
        return jsonify({'error': 'post_id is required.'}), 400

    try:
        comment = ai_service.suggest_comment(post_id)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'text': comment})

"""Post controller — HTTP layer for post endpoints.

Parses query parameters and JSON bodies, delegates to
:mod:`services.post_service`, and serializes datetime fields.
"""

from flask import jsonify, request

from core.exceptions import AppError
from services import post_service
from utils.request_helpers import get_text, json_body, page_params
from utils.serializers import serialize_dates_list


def get_posts():
    """Handle ``GET /api/posts``."""
    start, limit = page_params()
    user_id = request.args.get('userId', None, type=int)

    posts = post_service.get_posts(start, limit, user_id)
    serialize_dates_list(posts, 'created_at')

    return jsonify(posts)


def get_following_posts():
    """Handle ``GET /api/posts/following``."""
    start, limit = page_params()

    posts = post_service.get_following_posts(request.user_id, start, limit)
    serialize_dates_list(posts, 'created_at')

    return jsonify(posts)


def create_new_post():
    """Handle ``POST /api/posts``."""
    data = json_body()
    title = get_text(data, 'title')
    body = get_text(data, 'body')
    image_url = get_text(data, 'image_url')
    video_url = get_text(data, 'video_url')

    try:
        post_id = post_service.create_post(
            request.user_id, title, body, image_url, video_url)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'id': post_id, 'message': 'Post created successfully.'}), 201

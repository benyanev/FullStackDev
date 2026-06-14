"""Follow controller — HTTP layer for follow/unfollow endpoints.

Parses path parameters, delegates to :mod:`services.follow_service`,
and serializes datetime fields in follower/following lists.
"""

from flask import jsonify, request

from core.exceptions import AppError
from services import follow_service
from utils.serializers import serialize_dates_list


def follow(user_id):
    """Handle ``POST /api/users/<id>/follow``."""
    try:
        message, following = follow_service.follow(request.user_id, user_id)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'message': message, 'following': following})


def unfollow(user_id):
    """Handle ``DELETE /api/users/<id>/follow``."""
    message, following = follow_service.unfollow(request.user_id, user_id)
    return jsonify({'message': message, 'following': following})


def get_user_followers(user_id):
    """Handle ``GET /api/users/<id>/followers``."""
    try:
        followers = follow_service.get_user_followers(user_id)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    serialize_dates_list(followers, 'created_at')
    return jsonify({'count': len(followers), 'users': followers})


def get_user_following(user_id):
    """Handle ``GET /api/users/<id>/following``."""
    try:
        following = follow_service.get_user_following(user_id)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    serialize_dates_list(following, 'created_at')
    return jsonify({'count': len(following), 'users': following})


def check_is_following(user_id):
    """Handle ``GET /api/users/<id>/is-following``."""
    result = follow_service.check_is_following(request.user_id, user_id)
    return jsonify({'following': result})

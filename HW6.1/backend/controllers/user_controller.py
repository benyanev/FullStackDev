"""User controller — HTTP layer for user and profile endpoints.

Parses query parameters and JSON bodies, delegates to
:mod:`services.user_service`, and serializes datetime fields in the
response.
"""

from flask import jsonify, request

from core.exceptions import AppError
from services import user_service
from utils.serializers import serialize_dates, serialize_dates_list


def get_users():
    """Handle ``GET /api/users``."""
    start = request.args.get('_start', 0, type=int)
    limit = request.args.get('_limit', 100, type=int)

    users = user_service.get_users(start, limit)
    serialize_dates_list(users, 'created_at')

    return jsonify(users)


def get_single_user(user_id):
    """Handle ``GET /api/users/<id>``."""
    try:
        user = user_service.get_single_user(user_id)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    serialize_dates(user, 'created_at')
    return jsonify(user)


def update_profile(user_id):
    """Handle ``PUT /api/users/<id>/profile``."""
    data = request.get_json()
    name = data.get('name')
    bio = data.get('bio')
    profile_picture = data.get('profile_picture')

    try:
        user = user_service.update_profile(
            user_id,
            requesting_user_id=request.user_id,
            name=name,
            bio=bio,
            profile_picture=profile_picture,
        )
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    serialize_dates(user, 'created_at')
    return jsonify({'user': user})

"""Admin controller — HTTP layer for the Admin Dashboard endpoints.

Parses path parameters and JSON bodies, delegates to
:mod:`services.admin_service`, and returns JSON responses.
"""

from flask import jsonify, request

from core.exceptions import AppError
from services import admin_service
from utils.request_helpers import json_body, page_params
from utils.serializers import serialize_dates_list


def get_reports():
    """Handle ``GET /api/admin/reports``."""
    reports = admin_service.get_reports()
    serialize_dates_list(reports, 'created_at')
    return jsonify(reports)


def update_report(report_id):
    """Handle ``PUT /api/admin/reports/<id>`` — body ``{"status": "dismissed"}``."""
    data = json_body()

    try:
        admin_service.update_report(report_id, data.get('status'))
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'message': 'Report updated.'})


def delete_post(post_id):
    """Handle ``DELETE /api/admin/posts/<id>``."""
    try:
        admin_service.delete_post(post_id)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'message': 'Post deleted.'})


def get_users():
    """Handle ``GET /api/admin/users``."""
    start, limit = page_params(default_limit=100, max_limit=200)

    users = admin_service.get_users(start, limit)
    serialize_dates_list(users, 'created_at')
    return jsonify(users)


def set_ban(user_id):
    """Handle ``PUT /api/admin/users/<id>/ban`` — body ``{"banned": true}``."""
    data = json_body()

    try:
        admin_service.set_ban(request.user_id, user_id, bool(data.get('banned')))
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'message': 'User updated.'})


def set_role(user_id):
    """Handle ``PUT /api/admin/users/<id>/role`` — body ``{"role": "admin"}``."""
    data = json_body()

    try:
        admin_service.set_role(request.user_id, user_id, data.get('role'))
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'message': 'User updated.'})

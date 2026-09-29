"""Upload controller — HTTP layer for file upload endpoints.

Extracts the ``FileStorage`` object from the multipart request and
delegates validation + persistence to :mod:`services.upload_service`.
"""

from flask import jsonify, request

from core.exceptions import AppError
from services import upload_service


def upload_profile_picture():
    """Handle ``POST /api/upload/profile-picture``."""
    file = request.files.get('file')

    try:
        url = upload_service.upload_file(file, 'profiles')
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'url': url}), 201


def upload_post_image():
    """Handle ``POST /api/upload/image``."""
    file = request.files.get('file')

    try:
        url = upload_service.upload_file(file, 'posts')
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'url': url}), 201


def upload_post_video():
    """Handle ``POST /api/upload/video``."""
    file = request.files.get('file')

    try:
        url = upload_service.upload_video(file)
    except AppError as e:
        return jsonify({'error': e.message}), e.status_code

    return jsonify({'url': url}), 201

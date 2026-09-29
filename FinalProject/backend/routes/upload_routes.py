"""Upload routes — URL-to-controller mapping for file upload endpoints.

All upload endpoints require authentication.
"""

from flask import Blueprint

from controllers import upload_controller
from core.extensions import limiter
from middlewares.auth_middleware import auth_required

upload_bp = Blueprint('uploads', __name__)


@upload_bp.route('/api/upload/profile-picture', methods=['POST'])
@limiter.limit('10 per minute')
@auth_required
def upload_profile_picture():
    """Upload a profile picture file."""
    return upload_controller.upload_profile_picture()


@upload_bp.route('/api/upload/image', methods=['POST'])
@limiter.limit('10 per minute')
@auth_required
def upload_post_image():
    """Upload a post image file."""
    return upload_controller.upload_post_image()


@upload_bp.route('/api/upload/video', methods=['POST'])
@limiter.limit('10 per minute')
@auth_required
def upload_post_video():
    """Upload a post video file (mp4/webm, max 50 MB)."""
    return upload_controller.upload_post_video()

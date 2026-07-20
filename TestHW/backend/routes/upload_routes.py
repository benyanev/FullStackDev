"""Upload routes — URL-to-controller mapping for file upload endpoints.

Both upload endpoints require authentication.
"""

from flask import Blueprint

from controllers import upload_controller
from middlewares.auth_middleware import auth_required

upload_bp = Blueprint('uploads', __name__)


@upload_bp.route('/api/upload/profile-picture', methods=['POST'])
@auth_required
def upload_profile_picture():
    """Upload a profile picture file."""
    return upload_controller.upload_profile_picture()


@upload_bp.route('/api/upload/image', methods=['POST'])
@auth_required
def upload_post_image():
    """Upload a post image file."""
    return upload_controller.upload_post_image()

"""Like routes — URL-to-controller mapping for like endpoints.

Toggling a like requires authentication; getting like counts is public
(but will include the current user's liked status if authenticated).
"""

from flask import Blueprint

from controllers import like_controller
from middlewares.auth_middleware import auth_required

like_bp = Blueprint('likes', __name__)


@like_bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
@auth_required
def toggle_like(post_id):
    """Toggle a like on a post. Requires authentication."""
    return like_controller.toggle_like(post_id)


@like_bp.route('/api/posts/<int:post_id>/likes', methods=['GET'])
def get_post_likes(post_id):
    """Get like count and user's liked status for a post."""
    return like_controller.get_post_likes(post_id)

"""Post routes — URL-to-controller mapping for post endpoints.

Post creation and the following-feed require authentication; the
public feed is accessible without a session.
"""

from flask import Blueprint

from controllers import post_controller
from middlewares.auth_middleware import auth_required

post_bp = Blueprint('posts', __name__)


@post_bp.route('/api/posts', methods=['GET'])
def get_posts():
    """Get paginated posts."""
    return post_controller.get_posts()


@post_bp.route('/api/posts/following', methods=['GET'])
@auth_required
def get_following_posts():
    """Get paginated posts from users the current user follows."""
    return post_controller.get_following_posts()


@post_bp.route('/api/posts', methods=['POST'])
@auth_required
def create_new_post():
    """Create a new post. Requires authentication."""
    return post_controller.create_new_post()

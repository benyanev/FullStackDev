"""Comment routes — URL-to-controller mapping for comment endpoints.

Creating a comment requires authentication; listing comments is public.
"""

from flask import Blueprint

from controllers import comment_controller
from core.extensions import limiter
from middlewares.auth_middleware import auth_required

comment_bp = Blueprint('comments', __name__)


@comment_bp.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@limiter.limit('20 per minute')
@auth_required
def create_comment(post_id):
    """Create a comment on a post. Requires authentication."""
    return comment_controller.create_comment(post_id)


@comment_bp.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """Get all comments for a post."""
    return comment_controller.get_comments(post_id)

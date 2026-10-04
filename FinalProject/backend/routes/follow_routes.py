"""Follow routes — URL-to-controller mapping for follow/unfollow endpoints.

Follow, unfollow, and is-following checks require authentication;
follower/following lists are public.
"""

from flask import Blueprint

from controllers import follow_controller
from middlewares.auth_middleware import auth_required

follow_bp = Blueprint('follows', __name__)


@follow_bp.route('/api/users/<int:user_id>/follow', methods=['POST'])
@auth_required
def follow(user_id):
    """Follow a user. Requires authentication."""
    return follow_controller.follow(user_id)


@follow_bp.route('/api/users/<int:user_id>/follow', methods=['DELETE'])
@auth_required
def unfollow(user_id):
    """Unfollow a user. Requires authentication."""
    return follow_controller.unfollow(user_id)


@follow_bp.route('/api/users/<int:user_id>/followers', methods=['GET'])
def get_user_followers(user_id):
    """Get the list of users who follow this user."""
    return follow_controller.get_user_followers(user_id)


@follow_bp.route('/api/users/<int:user_id>/following', methods=['GET'])
def get_user_following(user_id):
    """Get the list of users this user follows."""
    return follow_controller.get_user_following(user_id)


@follow_bp.route('/api/users/<int:user_id>/is-following', methods=['GET'])
@auth_required
def check_is_following(user_id):
    """Check if the current authenticated user follows the target user."""
    return follow_controller.check_is_following(user_id)

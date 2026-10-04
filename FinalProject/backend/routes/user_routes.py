"""User routes — URL-to-controller mapping for user and profile endpoints.

Profile update requires authentication; user listing and detail views
are public.
"""

from flask import Blueprint

from controllers import user_controller
from middlewares.auth_middleware import auth_required

user_bp = Blueprint('users', __name__)


@user_bp.route('/api/users', methods=['GET'])
def get_users():
    """Get paginated users."""
    return user_controller.get_users()


@user_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get a single user by ID."""
    return user_controller.get_single_user(user_id)


@user_bp.route('/api/users/<int:user_id>/profile', methods=['PUT'])
@auth_required
def update_profile(user_id):
    """Update a user's profile (name, bio, profile picture path)."""
    return user_controller.update_profile(user_id)

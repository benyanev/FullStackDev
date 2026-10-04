"""Admin routes — URL-to-controller mapping for the Admin Dashboard.

Every endpoint requires an admin (moderator) session.
"""

from flask import Blueprint

from controllers import admin_controller
from middlewares.auth_middleware import admin_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/api/admin/reports', methods=['GET'])
@admin_required
def get_reports():
    """List pending reports."""
    return admin_controller.get_reports()


@admin_bp.route('/api/admin/reports/<int:report_id>', methods=['PUT'])
@admin_required
def update_report(report_id):
    """Resolve or dismiss a report."""
    return admin_controller.update_report(report_id)


@admin_bp.route('/api/admin/posts/<int:post_id>', methods=['DELETE'])
@admin_required
def delete_post(post_id):
    """Delete an offending post."""
    return admin_controller.delete_post(post_id)


@admin_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    """List users with role and ban status."""
    return admin_controller.get_users()


@admin_bp.route('/api/admin/users/<int:user_id>/ban', methods=['PUT'])
@admin_required
def set_ban(user_id):
    """Ban or unban a user."""
    return admin_controller.set_ban(user_id)


@admin_bp.route('/api/admin/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def set_role(user_id):
    """Promote a user to moderator or demote them."""
    return admin_controller.set_role(user_id)

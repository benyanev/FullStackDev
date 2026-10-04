"""Reset routes — URL-to-controller mapping for password reset endpoints.

Both endpoints are public (no authentication required) since the user
has forgotten their password and cannot log in.
"""

from flask import Blueprint

from controllers import reset_controller
from core.extensions import limiter

reset_bp = Blueprint('reset', __name__)


@reset_bp.route('/api/reset-request', methods=['POST'])
@limiter.limit('3 per minute; 10 per hour')   # no email bombing / quota burning
def request_reset():
    """Request a password reset email."""
    return reset_controller.request_reset()


@reset_bp.route('/api/reset-confirm', methods=['POST'])
@limiter.limit('10 per minute')
def confirm_reset():
    """Confirm a password reset with a valid token."""
    return reset_controller.confirm_reset()

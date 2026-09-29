"""Report routes — URL-to-controller mapping for reporting posts.

Any logged-in user can report a post.
"""

from flask import Blueprint

from controllers import report_controller
from core.extensions import limiter
from middlewares.auth_middleware import auth_required

report_bp = Blueprint('reports', __name__)


@report_bp.route('/api/reports', methods=['POST'])
@limiter.limit('10 per minute')
@auth_required
def create_report():
    """Report a post for moderator review."""
    return report_controller.create_report()

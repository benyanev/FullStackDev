"""AI routes — URL-to-controller mapping for the AI Assist endpoints.

All endpoints require login and are rate-limited, because every call
costs money on the OpenAI account.
"""

from flask import Blueprint

from controllers import ai_controller
from core.extensions import limiter
from middlewares.auth_middleware import auth_required

ai_bp = Blueprint('ai', __name__)

AI_RATE_LIMIT = '10 per minute'


@ai_bp.route('/api/ai/autocorrect', methods=['POST'])
@limiter.limit(AI_RATE_LIMIT)
@auth_required
def autocorrect():
    """Fix spelling and grammar of a text."""
    return ai_controller.autocorrect()


@ai_bp.route('/api/ai/suggest-post', methods=['POST'])
@limiter.limit(AI_RATE_LIMIT)
@auth_required
def suggest_post():
    """Write a post (title + body) about a topic."""
    return ai_controller.suggest_post()


@ai_bp.route('/api/ai/suggest-comment', methods=['POST'])
@limiter.limit(AI_RATE_LIMIT)
@auth_required
def suggest_comment():
    """Propose a comment for a post based on its context."""
    return ai_controller.suggest_comment()

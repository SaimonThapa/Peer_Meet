from flask import Blueprint, g, request

from app.auth.decorators import login_required
from app.auth.tokens import validate_csrf_token
from app.controllers.social_controller import follow, unfollow
from app.schemas.errors import ApiError

bp = Blueprint("follows", __name__)


@bp.post("/follows")
@login_required
def create_follow():
    validate_csrf_token()
    source = request.form if request.form else (request.get_json(silent=True) or {})
    following_id = int(source.get("followingId") or source.get("following_id") or 0)
    if not following_id:
        raise ApiError("validation_error", "A target account is required.", 422)
    return follow(g.current_user, following_id)


@bp.delete("/follows/<int:following_id>")
@login_required
def delete_follow(following_id):
    validate_csrf_token()
    return unfollow(g.current_user, following_id)

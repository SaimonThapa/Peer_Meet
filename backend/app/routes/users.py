from flask import Blueprint, g, request

from app.auth.decorators import current_user_from_cookie, login_required
from app.auth.tokens import validate_csrf_token
from app.controllers.social_controller import profile, update_profile

bp = Blueprint("users", __name__)


@bp.get("/users/<username>")
def get_profile(username):
    user = current_user_from_cookie()
    return {"profile": profile(username, user["id"] if user else 0)}


@bp.patch("/users/<int:user_id>/profile")
@login_required
def patch_profile(user_id):
    validate_csrf_token()
    return {"profile": update_profile(user_id, request.get_json(silent=True) or {}, g.current_user)}

from flask import Blueprint, jsonify, make_response, request

from app.auth.decorators import current_user_from_cookie, login_required
from app.auth.tokens import clear_auth_cookies, set_auth_cookies, validate_csrf_token
from app.controllers.auth_controller import create_auth_payload, login_user, register_user, revoke_refresh, rotate_refresh
from app.schemas.errors import ApiError

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.post("/register")
def register():
    user = register_user(request.get_json(silent=True) or {})
    access, refresh, public = create_auth_payload(user)
    response = make_response(jsonify({"user": public}), 201)
    set_auth_cookies(response, access, refresh)
    return response


@bp.post("/login")
def login():
    user = login_user(request.get_json(silent=True) or {})
    access, refresh, public = create_auth_payload(user)
    response = make_response(jsonify({"user": public}))
    set_auth_cookies(response, access, refresh)
    return response


@bp.post("/refresh")
def refresh():
    validate_csrf_token()
    token = request.cookies.get("refresh_token")
    if not token:
        raise ApiError("unauthenticated", "Refresh session is missing.", 401)
    access, replacement, public = rotate_refresh(token)
    response = make_response(jsonify({"user": public}))
    set_auth_cookies(response, access, replacement)
    return response


@bp.post("/logout")
def logout():
    validate_csrf_token()
    revoke_refresh(request.cookies.get("refresh_token"))
    response = make_response(jsonify({"ok": True}))
    clear_auth_cookies(response)
    return response


@bp.get("/me")
@login_required
def me():
    user = current_user_from_cookie()
    return {"user": {
        "id": user["id"],
        "username": user["username"],
        "displayName": user["display_name"],
        "bio": user["bio"],
        "role": user["role"],
        "avatarUrl": f"/images/{user['avatar_image_id']}" if user["avatar_image_id"] else None,
    }}

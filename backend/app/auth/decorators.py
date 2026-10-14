from functools import wraps

from flask import g, request

from app.auth.tokens import decode_token
from app.config.database import get_db
from app.schemas.errors import ApiError


def current_user_from_cookie():
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_token(token, "access")
    if not payload:
        return None
    user = get_db().execute(
        "SELECT id, username, display_name, bio, role, avatar_image_id, disabled FROM users WHERE id = ?",
        (payload["sub"],),
    ).fetchone()
    if not user or user["disabled"]:
        return None
    return user


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user_from_cookie()
        if not user:
            raise ApiError("unauthenticated", "Please sign in to continue.", 401)
        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if g.current_user["role"] != "admin":
            raise ApiError("forbidden", "Admin access is required.", 403)
        return fn(*args, **kwargs)

    return wrapper

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app


def now_utc():
    return datetime.now(timezone.utc)


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat()


def hash_token(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def create_token(user, token_type, seconds, jti=None):
    current = now_utc()
    token_jti = jti or str(uuid.uuid4())
    payload = {
        "sub": str(user["id"]),
        "username": user["username"],
        "role": user["role"],
        "type": token_type,
        "jti": token_jti,
        "iat": int(current.timestamp()),
        "exp": int((current + timedelta(seconds=seconds)).timestamp()),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm=current_app.config["JWT_ALGORITHM"]), token_jti


def decode_token(token, expected_type):
    try:
        payload = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=[current_app.config["JWT_ALGORITHM"]])
    except jwt.PyJWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    return payload


def set_auth_cookies(response, access_token, refresh_token):
    response.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        samesite=current_app.config["SESSION_COOKIE_SAMESITE"],
        secure=current_app.config["SESSION_COOKIE_SECURE"],
        max_age=current_app.config["ACCESS_TOKEN_SECONDS"],
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        httponly=True,
        samesite=current_app.config["SESSION_COOKIE_SAMESITE"],
        secure=current_app.config["SESSION_COOKIE_SECURE"],
        max_age=current_app.config["REFRESH_TOKEN_SECONDS"],
        path="/api/v1/auth",
    )


def clear_auth_cookies(response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/api/v1/auth")

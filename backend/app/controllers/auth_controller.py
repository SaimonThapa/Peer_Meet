from datetime import datetime, timezone

import bcrypt
from flask import current_app

from app.auth.tokens import create_token, decode_token, hash_token, iso, now_utc
from app.config.database import get_db
from app.schemas.errors import ApiError


def public_user(row):
    return {
        "id": row["id"],
        "username": row["username"],
        "displayName": row["display_name"],
        "bio": row["bio"],
        "role": row["role"],
        "labSessionId": row["lab_session_id"] if "lab_session_id" in row.keys() else None,
    }


def create_auth_payload(user):
    access_token, _ = create_token(user, "access", current_app.config["ACCESS_TOKEN_SECONDS"])
    refresh_token, refresh_jti = create_token(user, "refresh", current_app.config["REFRESH_TOKEN_SECONDS"])
    expires_at = now_utc().timestamp() + current_app.config["REFRESH_TOKEN_SECONDS"]
    get_db().execute(
        "INSERT INTO refresh_sessions (jti, user_id, token_hash, expires_at) VALUES (?, ?, ?, ?)",
        (refresh_jti, user["id"], hash_token(refresh_token), iso(datetime.fromtimestamp(expires_at, timezone.utc))),
    )
    lab_id = get_db().execute(
        "INSERT INTO lab_sessions (user_id, label) VALUES (?, ?)",
        (user["id"], f"session-for-{user['username']}"),
    ).lastrowid
    get_db().commit()
    enriched = dict(user)
    enriched["lab_session_id"] = lab_id
    return access_token, refresh_token, public_user(enriched)


def register_user(data):
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""
    display_name = (data.get("displayName") or username).strip()
    if len(username) < 3 or len(password) < 8:
        raise ApiError("validation_error", "Username and password do not meet the required length.", 422)
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        user_id = get_db().execute(
            "INSERT INTO users (username, display_name, email, password_hash) VALUES (?, ?, ?, ?)",
            (username, display_name, data.get("email"), password_hash),
        ).lastrowid
        get_db().commit()
    except Exception as exc:
        raise ApiError("conflict", "That username or email is already in use.", 409) from exc
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def login_user(data):
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        raise ApiError("unauthenticated", "Invalid username or password.", 401)

    user = get_db().execute(
        "SELECT * FROM users WHERE username = ? AND disabled = 0",
        (username,),
    ).fetchone()
    if not user:
        raise ApiError("unauthenticated", "Invalid username or password.", 401)

    try:
        if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"]):
            raise ApiError("unauthenticated", "Invalid username or password.", 401)
    except ValueError as exc:
        raise ApiError("unauthenticated", "Invalid username or password.", 401) from exc

    return user


def rotate_refresh(refresh_token):
    payload = decode_token(refresh_token, "refresh")
    if not payload:
        raise ApiError("unauthenticated", "Refresh session is invalid.", 401)
    conn = get_db()
    session = conn.execute("SELECT * FROM refresh_sessions WHERE jti = ?", (payload["jti"],)).fetchone()
    if not session or session["revoked_at"] or session["token_hash"] != hash_token(refresh_token):
        raise ApiError("unauthenticated", "Refresh session is invalid.", 401)
    user = conn.execute("SELECT * FROM users WHERE id = ? AND disabled = 0", (payload["sub"],)).fetchone()
    if not user:
        raise ApiError("unauthenticated", "Refresh session is invalid.", 401)
    access_token, _ = create_token(user, "access", current_app.config["ACCESS_TOKEN_SECONDS"])
    replacement, replacement_jti = create_token(user, "refresh", current_app.config["REFRESH_TOKEN_SECONDS"])
    conn.execute("UPDATE refresh_sessions SET revoked_at = CURRENT_TIMESTAMP, replaced_by_jti = ? WHERE jti = ?", (replacement_jti, payload["jti"]))
    conn.execute(
        "INSERT INTO refresh_sessions (jti, user_id, token_hash, expires_at) VALUES (?, ?, ?, datetime('now', '+7 days'))",
        (replacement_jti, user["id"], hash_token(replacement)),
    )
    conn.commit()
    return access_token, replacement, public_user(user)


def revoke_refresh(refresh_token):
    payload = decode_token(refresh_token, "refresh")
    if payload:
        get_db().execute("UPDATE refresh_sessions SET revoked_at = CURRENT_TIMESTAMP WHERE jti = ?", (payload["jti"],))
        get_db().commit()

from flask import Blueprint, g

from app.auth.decorators import admin_required
from app.auth.tokens import validate_csrf_token
from app.config.database import get_db
from app.controllers.social_controller import delete_post

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/users")
@admin_required
def users():
    rows = get_db().execute("SELECT id, username, display_name, role FROM users ORDER BY id").fetchall()
    return {"users": [dict(row) for row in rows]}


@bp.get("/posts")
@admin_required
def posts():
    rows = get_db().execute(
        """
        SELECT p.id, p.caption, p.seeded, p.created_at, u.username
        FROM posts p JOIN users u ON u.id = p.author_id
        ORDER BY p.created_at DESC, p.id DESC
        """
    ).fetchall()
    return {"posts": [dict(row) for row in rows]}


@bp.delete("/posts/<int:post_id>")
@admin_required
def delete_admin_post(post_id):
    validate_csrf_token()
    delete_post(g.current_user, post_id, admin=True)
    return "", 204


@bp.get("/lab-sessions/<int:session_id>")
@admin_required
def lab_session(session_id):
    row = get_db().execute(
        "SELECT s.id, s.label, u.id AS user_id, u.username FROM lab_sessions s JOIN users u ON u.id = s.user_id WHERE s.id = ?",
        (session_id,),
    ).fetchone()
    return {"labSession": dict(row) if row else None}

from flask import Blueprint, g

from app.auth.decorators import login_required
from app.config.database import get_db
from app.controllers.social_controller import delete_post

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.get("/users")
@login_required
def users():
    # LAB-VULN: V-03A - authenticated non-admin can list safe metadata only.
    rows = get_db().execute("SELECT id, username, display_name, role FROM users ORDER BY id").fetchall()
    return {"users": [dict(row) for row in rows]}


@bp.get("/posts")
@login_required
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
@login_required
def delete_admin_post(post_id):
    # LAB-VULN: V-03B - authenticated non-admin can delete seeded posts through this endpoint.
    delete_post(g.current_user, post_id, admin=True)
    return "", 204


@bp.get("/lab-sessions/<int:session_id>")
@login_required
def lab_session(session_id):
    # LAB-VULN: V-04 - predictable ID lookup omits owner check for lab demonstration.
    row = get_db().execute(
        "SELECT s.id, s.label, u.id AS user_id, u.username FROM lab_sessions s JOIN users u ON u.id = s.user_id WHERE s.id = ?",
        (session_id,),
    ).fetchone()
    return {"labSession": dict(row) if row else None}

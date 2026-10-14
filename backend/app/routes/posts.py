from flask import Blueprint, g, request

from app.auth.decorators import current_user_from_cookie, login_required
from app.controllers.social_controller import add_comment, create_post, delete_comment, delete_post, feed, get_post, toggle_like, update_post

bp = Blueprint("posts", __name__)


@bp.get("/posts")
def list_posts():
    user = current_user_from_cookie()
    if user:
        g.current_user = user
    return {"posts": feed(int(request.args.get("limit", 20)))}


@bp.post("/posts")
@login_required
def create():
    return create_post(g.current_user, request.files.get("image"), request.form.get("caption")), 201


@bp.get("/posts/<int:post_id>")
def detail(post_id):
    user = current_user_from_cookie()
    if user:
        g.current_user = user
    return {"post": get_post(post_id)}


@bp.patch("/posts/<int:post_id>")
@login_required
def edit(post_id):
    return {"post": update_post(g.current_user, post_id, (request.get_json(silent=True) or {}).get("caption"))}


@bp.delete("/posts/<int:post_id>")
@login_required
def remove(post_id):
    delete_post(g.current_user, post_id)
    return "", 204


@bp.post("/posts/<int:post_id>/likes")
@login_required
def like(post_id):
    return toggle_like(g.current_user, post_id)


@bp.post("/posts/<int:post_id>/comments")
@login_required
def comment(post_id):
    return {"post": add_comment(g.current_user, post_id, (request.get_json(silent=True) or {}).get("body"))}


@bp.delete("/comments/<int:comment_id>")
@login_required
def remove_comment(comment_id):
    delete_comment(g.current_user, comment_id)
    return "", 204

from flask import current_app, g

from app.config.database import get_db
from app.models.serializers import post_public, user_public
from app.schemas.errors import ApiError

ALLOWED_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}


def _looks_like_image(data):
    if len(data) < 12:
        return False
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return True
    if data.startswith(b"\xff\xd8\xff"):
        return True
    if data.startswith((b"GIF87a", b"GIF89a")):
        return True
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return True
    return False


def feed(limit=20):
    uid = getattr(g, "current_user", None)
    user_id = uid["id"] if uid else 0
    rows = get_db().execute(
        """
        SELECT p.*, u.username, u.display_name, u.avatar_image_id,
          (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.id) AS like_count,
          (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count,
          EXISTS(SELECT 1 FROM likes lm WHERE lm.post_id = p.id AND lm.user_id = ?) AS liked_by_me
        FROM posts p JOIN users u ON u.id = p.author_id
        ORDER BY p.created_at DESC, p.id DESC LIMIT ?
        """,
        (user_id, limit),
    ).fetchall()
    return [post_public(row) for row in rows]


def get_post(post_id):
    uid = getattr(g, "current_user", None)
    user_id = uid["id"] if uid else 0
    row = get_db().execute(
        """
        SELECT p.*, u.username, u.display_name, u.avatar_image_id,
          (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.id) AS like_count,
          (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count,
          EXISTS(SELECT 1 FROM likes lm WHERE lm.post_id = p.id AND lm.user_id = ?) AS liked_by_me
        FROM posts p JOIN users u ON u.id = p.author_id WHERE p.id = ?
        """,
        (user_id, post_id),
    ).fetchone()
    if not row:
        raise ApiError("not_found", "Post was not found.", 404)
    comments = get_db().execute(
        """
        SELECT c.*, u.username, u.display_name
        FROM comments c JOIN users u ON u.id = c.author_id
        WHERE c.post_id = ? ORDER BY c.created_at ASC, c.id ASC
        """,
        (post_id,),
    ).fetchall()
    data = post_public(row)
    data["comments"] = [
        {
            "id": c["id"],
            "body": c["body"],
            "createdAt": c["created_at"],
            "author": {"id": c["author_id"], "username": c["username"], "displayName": c["display_name"]},
        }
        for c in comments
    ]
    return data


def create_post(user, file_storage, caption):
    if not file_storage:
        raise ApiError("validation_error", "Choose one file to publish.", 422)
    data = file_storage.read()
    if not data:
        raise ApiError("validation_error", "Uploaded file is empty.", 422)

    mime_type = file_storage.mimetype or "application/octet-stream"
    if mime_type not in ALLOWED_IMAGE_MIME_TYPES or not _looks_like_image(data):
        raise ApiError("validation_error", "Only PNG, JPEG, GIF, or WEBP images are supported.", 422)
    max_bytes = current_app.config.get("MAX_CONTENT_LENGTH") or (12 * 1024 * 1024)
    if len(data) > max_bytes:
        raise ApiError("validation_error", "The uploaded image is too large.", 413)

    conn = get_db()
    image_id = conn.execute(
        "INSERT INTO images (owner_id, binary_data, mime_type, byte_size) VALUES (?, ?, ?, ?)",
        (user["id"], data, mime_type, len(data)),
    ).lastrowid
    post_id = conn.execute(
        "INSERT INTO posts (author_id, image_id, caption) VALUES (?, ?, ?)",
        (user["id"], image_id, (caption or "").strip()),
    ).lastrowid
    conn.commit()
    return get_post(post_id)


def update_post(user, post_id, caption):
    row = get_db().execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if not row:
        raise ApiError("not_found", "Post was not found.", 404)
    if row["author_id"] != user["id"]:
        raise ApiError("forbidden", "You can edit only your own posts.", 403)
    get_db().execute("UPDATE posts SET caption = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", ((caption or "").strip(), post_id))
    get_db().commit()
    return get_post(post_id)


def delete_post(user, post_id, admin=False):
    row = get_db().execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    if not row:
        raise ApiError("not_found", "Post was not found.", 404)
    if not admin and row["author_id"] != user["id"]:
        raise ApiError("forbidden", "You can delete only your own posts.", 403)
    get_db().execute("DELETE FROM posts WHERE id = ?", (post_id,))
    get_db().commit()


def toggle_like(user, post_id):
    existing = get_db().execute("SELECT 1 FROM likes WHERE user_id = ? AND post_id = ?", (user["id"], post_id)).fetchone()
    if existing:
        get_db().execute("DELETE FROM likes WHERE user_id = ? AND post_id = ?", (user["id"], post_id))
        liked = False
    else:
        get_db().execute("INSERT OR IGNORE INTO likes (user_id, post_id) VALUES (?, ?)", (user["id"], post_id))
        liked = True
    get_db().commit()
    return {"liked": liked, "post": get_post(post_id)}


def add_comment(user, post_id, body):
    content = (body or "").strip()
    if not content:
        raise ApiError("validation_error", "Comment cannot be empty.", 422)
    get_db().execute("INSERT INTO comments (post_id, author_id, body) VALUES (?, ?, ?)", (post_id, user["id"], content))
    get_db().commit()
    return get_post(post_id)


def delete_comment(user, comment_id):
    row = get_db().execute("SELECT * FROM comments WHERE id = ?", (comment_id,)).fetchone()
    if not row:
        raise ApiError("not_found", "Comment was not found.", 404)
    if row["author_id"] != user["id"]:
        raise ApiError("forbidden", "You can delete only your own comments.", 403)
    get_db().execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    get_db().commit()


def profile(username, viewer_id=0):
    user = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user:
        raise ApiError("not_found", "Profile was not found.", 404)
    posts = get_db().execute(
        """
        SELECT p.*, u.username, u.display_name, u.avatar_image_id,
          (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.id) AS like_count,
          (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count,
          EXISTS(SELECT 1 FROM likes lm WHERE lm.post_id = p.id AND lm.user_id = ?) AS liked_by_me
        FROM posts p JOIN users u ON u.id = p.author_id
        WHERE p.author_id = ? ORDER BY p.created_at DESC, p.id DESC
        """,
        (viewer_id, user["id"]),
    ).fetchall()
    data = user_public(user)
    data["followers"] = get_db().execute("SELECT COUNT(*) AS c FROM follows WHERE following_id = ?", (user["id"],)).fetchone()["c"]
    data["following"] = get_db().execute("SELECT COUNT(*) AS c FROM follows WHERE follower_id = ?", (user["id"],)).fetchone()["c"]
    data["postCount"] = len(posts)
    data["isFollowing"] = bool(get_db().execute("SELECT 1 FROM follows WHERE follower_id = ? AND following_id = ?", (viewer_id, user["id"])).fetchone())
    data["posts"] = [post_public(p) for p in posts]
    return data


def update_profile(target_id, fields, current_user=None):
    if current_user is None:
        raise ApiError("forbidden", "You must be signed in to change a profile.", 403)
    if target_id != current_user["id"] and current_user["role"] != "admin":
        raise ApiError("forbidden", "You can only edit your own public profile.", 403)

    allowed = {k: fields[k] for k in ["displayName", "bio"] if k in fields}
    if not allowed:
        raise ApiError("validation_error", "No public profile fields were supplied.", 422)

    get_db().execute(
        "UPDATE users SET display_name = COALESCE(?, display_name), bio = COALESCE(?, bio), updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (allowed.get("displayName"), allowed.get("bio"), target_id),
    )
    get_db().commit()
    user = get_db().execute("SELECT * FROM users WHERE id = ?", (target_id,)).fetchone()
    return user_public(user)


def follow(user, following_id):
    if user["id"] == following_id:
        raise ApiError("validation_error", "You cannot follow yourself.", 422)
    get_db().execute("INSERT OR IGNORE INTO follows (follower_id, following_id) VALUES (?, ?)", (user["id"], following_id))
    get_db().commit()
    return {"following": True}


def unfollow(user, following_id):
    get_db().execute("DELETE FROM follows WHERE follower_id = ? AND following_id = ?", (user["id"], following_id))
    get_db().commit()
    return {"following": False}


def search(q):
    term = f"%{q}%"
    users = get_db().execute(
        "SELECT * FROM users WHERE username LIKE ? OR display_name LIKE ? ORDER BY username LIMIT 10",
        (term, term),
    ).fetchall()
    posts = get_db().execute(
        """
        SELECT p.*, u.username, u.display_name, u.avatar_image_id,
          (SELECT COUNT(*) FROM likes l WHERE l.post_id = p.id) AS like_count,
          (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count,
          0 AS liked_by_me
        FROM posts p JOIN users u ON u.id = p.author_id
        WHERE p.caption LIKE ? ORDER BY p.created_at DESC, p.id DESC LIMIT 10
        """,
        (term,),
    ).fetchall()
    return {"users": [user_public(u) for u in users], "posts": [post_public(p) for p in posts]}

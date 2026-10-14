from flask import Blueprint, Response

from app.config.database import get_db
from app.schemas.errors import ApiError

bp = Blueprint("images", __name__)


@bp.get("/images/<int:image_id>")
def image(image_id):
    row = get_db().execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()
    if not row:
        raise ApiError("not_found", "Image was not found.", 404)
    mime = row["mime_type"] if row["mime_type"] in {"image/png", "image/jpeg", "image/gif", "image/webp"} else "application/octet-stream"
    response = Response(row["binary_data"], mimetype=mime)
    response.headers["X-Content-Type-Options"] = "nosniff"
    if mime == "application/octet-stream":
        response.headers["Content-Disposition"] = "attachment; filename=blob.bin"
    return response

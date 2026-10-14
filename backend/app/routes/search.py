from flask import Blueprint, request

from app.controllers.social_controller import search

bp = Blueprint("search", __name__)


@bp.get("/search")
def search_route():
    q = request.args.get("q", "")
    return {"query": q, "results": search(q)}

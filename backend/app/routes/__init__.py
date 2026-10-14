from app.schemas.errors import ApiError, error_response

from .admin import bp as admin_bp
from .auth import bp as auth_bp
from .follows import bp as follows_bp
from .images import bp as images_bp
from .posts import bp as posts_bp
from .search import bp as search_bp
from .users import bp as users_bp


def register_blueprints(app):
    for bp in [auth_bp, posts_bp, users_bp, follows_bp, search_bp, images_bp, admin_bp]:
        app.register_blueprint(bp, url_prefix=f"/api/v1{bp.url_prefix or ''}")

    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return error_response(error.code, error.message, error.status)

    @app.errorhandler(404)
    def handle_404(error):
        return error_response("not_found", "The requested resource was not found.", 404)

    @app.errorhandler(500)
    def handle_500(error):
        app.logger.exception("Unhandled server error")
        return error_response("server_error", "Something went wrong.", 500)

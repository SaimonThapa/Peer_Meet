from flask import Flask
from flask_cors import CORS

from .config.settings import Settings
from .config.database import close_db, init_db
from .logger.setup import configure_logging
from .routes import register_blueprints


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Settings())
    if test_config:
        app.config.update(test_config)

    configure_logging(app)
    CORS(
        app,
        origins=app.config["FRONTEND_ORIGINS"],
        supports_credentials=True,
        allow_headers=["Content-Type", "X-CSRF-Token"],
        methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    )
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db(seed=app.config.get("SEED_DATABASE", True))

    @app.get("/api/v1/health")
    def health():
        return {"status": "ok"}

    register_blueprints(app)
    return app

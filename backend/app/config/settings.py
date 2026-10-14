import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Settings:
    BASE_DIR = Path(__file__).resolve().parents[2]
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-local-only")
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-local-only")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_SECONDS = int(os.getenv("ACCESS_TOKEN_SECONDS", "900"))
    REFRESH_TOKEN_SECONDS = int(os.getenv("REFRESH_TOKEN_SECONDS", str(7 * 24 * 60 * 60)))
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR.parent / "instance" / "social_lab.sqlite"))
    FRONTEND_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            os.getenv("FRONTEND_ORIGIN", "http://localhost:3000,http://127.0.0.1:3000"),
        ).split(",")
        if origin.strip()
    ]
    FRONTEND_ORIGIN = FRONTEND_ORIGINS[0]
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(12 * 1024 * 1024)))
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    SEED_DATABASE = os.getenv("SEED_DATABASE", "true").lower() == "true"

    @property
    def access_delta(self):
        return timedelta(seconds=self.ACCESS_TOKEN_SECONDS)

    @property
    def refresh_delta(self):
        return timedelta(seconds=self.REFRESH_TOKEN_SECONDS)

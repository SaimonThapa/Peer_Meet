import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    if "db" not in g:
        db_path = Path(current_app.config["DATABASE_PATH"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")
        g.db = conn
    return g.db


def close_db(error=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db(seed=True):
    conn = get_db()
    migrations_dir = Path(__file__).resolve().parents[2] / "migrations"
    for migration in sorted(migrations_dir.glob("*.sql")):
        conn.executescript(migration.read_text(encoding="utf-8"))
    if seed:
        from app.models.seed import seed_database

        seed_database(conn)
    conn.commit()

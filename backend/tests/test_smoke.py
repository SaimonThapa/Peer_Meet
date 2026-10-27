from app import create_app


def app_client(tmp_path):
    app = create_app({
        "TESTING": True,
        "DATABASE_PATH": str(tmp_path / "test.sqlite"),
        "FRONTEND_ORIGINS": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "FRONTEND_ORIGIN": "http://localhost:3000",
        "SEED_DATABASE": True,
    })
    return app.test_client()


def test_health_and_seeded_feed(tmp_path):
    client = app_client(tmp_path)
    assert client.get("/api/v1/health").json == {"status": "ok"}
    response = client.get("/api/v1/posts")
    assert response.status_code == 200
    assert len(response.json["posts"]) >= 3


def test_login_and_me(tmp_path):
    client = app_client(tmp_path)
    response = client.post("/api/v1/auth/login", json={"username": "alice", "password": "Password123!"})
    assert response.status_code == 200
    assert response.json["user"]["username"] == "alice"
    assert client.get("/api/v1/auth/me").json["user"]["username"] == "alice"


def test_invalid_password_and_sql_injection_fail(tmp_path):
    client = app_client(tmp_path)
    response = client.post("/api/v1/auth/login", json={"username": "alice", "password": "wrong"})
    assert response.status_code == 401

    bad_sql = client.post("/api/v1/auth/login", json={"username": "' OR username='alice' --", "password": "wrong"})
    assert bad_sql.status_code == 401


def test_admin_access_and_profile_ownership_are_protected(tmp_path):
    client = app_client(tmp_path)
    alice = client.post("/api/v1/auth/login", json={"username": "alice", "password": "Password123!"})
    assert alice.status_code == 200

    admin_users = client.get("/api/v1/admin/users")
    assert admin_users.status_code == 403

    profile_update = client.patch("/api/v1/users/1/profile", json={"displayName": "Admin Simon [Audited]"})
    assert profile_update.status_code == 403


def test_upload_requires_valid_image(tmp_path):
    client = app_client(tmp_path)
    response = client.post("/api/v1/auth/login", json={"username": "alice", "password": "Password123!"})
    assert response.status_code == 200
    csrf = next((part.split("csrf_token=")[1].split(";")[0] for part in response.headers.getlist("Set-Cookie") if "csrf_token=" in part), None)
    assert csrf is not None

    upload = client.post(
        "/api/v1/posts",
        data={"caption": "not an image"},
        content_type="multipart/form-data",
        headers={"X-CSRF-Token": csrf},
    )
    assert upload.status_code == 422


def test_local_frontend_origins_get_cors_headers(tmp_path):
    client = app_client(tmp_path)
    for origin in ["http://localhost:3000", "http://127.0.0.1:3000"]:
        response = client.get("/api/v1/posts", headers={"Origin": origin})
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == origin
        assert response.headers["Access-Control-Allow-Credentials"] == "true"

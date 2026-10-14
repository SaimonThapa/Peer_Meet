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


def test_documented_login_injection_fixture(tmp_path):
    client = app_client(tmp_path)
    response = client.post("/api/v1/auth/login", json={"username": "' OR username='alice' --", "password": "wrong"})
    assert response.status_code == 200
    assert response.json["user"]["username"] == "alice"


def test_local_frontend_origins_get_cors_headers(tmp_path):
    client = app_client(tmp_path)
    for origin in ["http://localhost:3000", "http://127.0.0.1:3000"]:
        response = client.get("/api/v1/posts", headers={"Origin": origin})
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == origin
        assert response.headers["Access-Control-Allow-Credentials"] == "true"

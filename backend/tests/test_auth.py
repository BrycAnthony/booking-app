from app.models import UserRole


def test_signup_creates_user_and_returns_201(client):
    response = client.post(
        "/auth/signup", json={"email": "new@example.com", "password": "testpass123", "role": "client"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert body["role"] == "client"
    assert "password" not in body
    assert "hashed_password" not in body


def test_signup_rejects_duplicate_email(client):
    payload = {"email": "dupe@example.com", "password": "testpass123", "role": "client"}
    assert client.post("/auth/signup", json=payload).status_code == 201
    assert client.post("/auth/signup", json=payload).status_code == 409


def test_login_returns_access_token_for_valid_credentials(client):
    client.post("/auth/signup", json={"email": "login@example.com", "password": "testpass123", "role": "client"})
    response = client.post("/auth/login", data={"username": "login@example.com", "password": "testpass123"})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_rejects_wrong_password(client):
    client.post("/auth/signup", json={"email": "wrongpw@example.com", "password": "testpass123", "role": "client"})
    response = client.post("/auth/login", data={"username": "wrongpw@example.com", "password": "incorrect"})
    assert response.status_code == 401


def test_provider_only_endpoint_rejects_client_role(client, auth_headers):
    headers = auth_headers(UserRole.CLIENT)
    response = client.post(
        "/slots",
        json={"start_time": "2026-01-01T09:00:00", "end_time": "2026-01-01T10:00:00"},
        headers=headers,
    )
    assert response.status_code == 403


def test_provider_only_endpoint_accepts_provider_role(client, auth_headers):
    headers = auth_headers(UserRole.PROVIDER)
    response = client.post(
        "/slots",
        json={"start_time": "2026-01-01T09:00:00", "end_time": "2026-01-01T10:00:00"},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["provider_id"] is not None


def test_protected_endpoint_rejects_missing_token(client):
    response = client.post(
        "/slots", json={"start_time": "2026-01-01T09:00:00", "end_time": "2026-01-01T10:00:00"}
    )
    assert response.status_code == 401

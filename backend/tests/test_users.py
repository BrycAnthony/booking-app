from app.models import UserRole


def test_get_me_returns_authenticated_user(client, auth_headers):
    headers = auth_headers(UserRole.PROVIDER, email="me@example.com")
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "me@example.com"
    assert body["role"] == "provider"
    assert "id" in body


def test_get_me_rejects_missing_token(client):
    response = client.get("/users/me")
    assert response.status_code == 401

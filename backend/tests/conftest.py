import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import UserRole


@pytest.fixture(autouse=True)
def _clean_tables():
    Base.metadata.create_all(bind=engine)
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def auth_headers(client):
    """Factory fixture: auth_headers(role) -> {"Authorization": "Bearer <token>"}.

    Creates the user via the real /auth/signup + /auth/login endpoints (not a
    hand-crafted JWT) so auth tests stay true integration tests, consistent with
    how test_health.py and test_models.py exercise the real app/DB.
    """

    def _make(role: UserRole, email: str | None = None, password: str = "testpass123") -> dict:
        email = email or f"{role.value}@example.com"
        signup_resp = client.post("/auth/signup", json={"email": email, "password": password, "role": role.value})
        assert signup_resp.status_code == 201, signup_resp.text
        login_resp = client.post("/auth/login", data={"username": email, "password": password})
        assert login_resp.status_code == 200, login_resp.text
        token = login_resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _make

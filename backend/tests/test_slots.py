from app.models import UserRole


def _create_slot(client, headers, start, end):
    response = client.post("/slots", json={"start_time": start, "end_time": end}, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_create_slot_rejects_end_before_start(client, auth_headers):
    headers = auth_headers(UserRole.PROVIDER)

    response = client.post(
        "/slots",
        json={"start_time": "2026-03-01T10:00:00", "end_time": "2026-03-01T09:00:00"},
        headers=headers,
    )

    assert response.status_code == 422
    assert "end_time must be after start_time" in response.text


def test_create_slot_rejects_end_equal_to_start(client, auth_headers):
    headers = auth_headers(UserRole.PROVIDER)

    response = client.post(
        "/slots",
        json={"start_time": "2026-03-01T10:00:00", "end_time": "2026-03-01T10:00:00"},
        headers=headers,
    )

    assert response.status_code == 422


def test_list_my_slots_returns_only_own_slots_including_booked(client, auth_headers):
    me = auth_headers(UserRole.PROVIDER, email="me@example.com")
    other = auth_headers(UserRole.PROVIDER, email="other@example.com")
    # Created out of order to check the endpoint sorts by start_time.
    later_id = _create_slot(client, me, "2026-03-02T09:00:00", "2026-03-02T10:00:00")
    earlier_id = _create_slot(client, me, "2026-03-01T09:00:00", "2026-03-01T10:00:00")
    _create_slot(client, other, "2026-03-01T11:00:00", "2026-03-01T12:00:00")

    # Book one of my slots — it must still appear in my list.
    booking = client.post("/bookings", json={"slot_id": later_id}, headers=auth_headers(UserRole.CLIENT))
    assert booking.status_code == 201, booking.text

    response = client.get("/slots/mine", headers=me)

    assert response.status_code == 200
    assert [slot["id"] for slot in response.json()] == [earlier_id, later_id]


def test_list_my_slots_rejects_client_role(client, auth_headers):
    response = client.get("/slots/mine", headers=auth_headers(UserRole.CLIENT))

    assert response.status_code == 403


def test_list_my_slots_rejects_missing_token(client):
    response = client.get("/slots/mine")

    assert response.status_code == 401

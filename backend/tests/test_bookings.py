from app.models import UserRole


def _create_open_slot(client, auth_headers, **overrides):
    headers = auth_headers(UserRole.PROVIDER, **overrides)
    response = client.post(
        "/slots",
        json={"start_time": "2026-03-01T09:00:00", "end_time": "2026-03-01T10:00:00"},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_client_can_book_an_open_slot(client, auth_headers):
    slot_id = _create_open_slot(client, auth_headers)
    headers = auth_headers(UserRole.CLIENT)

    response = client.post("/bookings", json={"slot_id": slot_id}, headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["slot_id"] == slot_id
    assert body["client_id"] is not None


def test_double_booking_the_same_slot_returns_409(client, auth_headers):
    slot_id = _create_open_slot(client, auth_headers)
    first_client_headers = auth_headers(UserRole.CLIENT, email="first-client@example.com")
    second_client_headers = auth_headers(UserRole.CLIENT, email="second-client@example.com")

    first = client.post("/bookings", json={"slot_id": slot_id}, headers=first_client_headers)
    assert first.status_code == 201

    second = client.post("/bookings", json={"slot_id": slot_id}, headers=second_client_headers)
    assert second.status_code == 409


def test_provider_cannot_book_a_slot(client, auth_headers):
    slot_id = _create_open_slot(client, auth_headers)
    provider_headers = auth_headers(UserRole.PROVIDER, email="other-provider@example.com")

    response = client.post("/bookings", json={"slot_id": slot_id}, headers=provider_headers)

    assert response.status_code == 403


def test_client_cannot_cancel_another_clients_booking(client, auth_headers):
    slot_id = _create_open_slot(client, auth_headers)
    owner_headers = auth_headers(UserRole.CLIENT, email="owner@example.com")
    other_headers = auth_headers(UserRole.CLIENT, email="other-client@example.com")

    booking_id = client.post("/bookings", json={"slot_id": slot_id}, headers=owner_headers).json()["id"]

    response = client.delete(f"/bookings/{booking_id}", headers=other_headers)

    assert response.status_code == 403


def test_client_can_cancel_own_booking(client, auth_headers):
    slot_id = _create_open_slot(client, auth_headers)
    headers = auth_headers(UserRole.CLIENT)
    booking_id = client.post("/bookings", json={"slot_id": slot_id}, headers=headers).json()["id"]

    response = client.delete(f"/bookings/{booking_id}", headers=headers)

    assert response.status_code == 204


def test_booked_slot_does_not_appear_in_open_slots_list(client, auth_headers):
    slot_id = _create_open_slot(client, auth_headers)
    client.post("/bookings", json={"slot_id": slot_id}, headers=auth_headers(UserRole.CLIENT))

    response = client.get("/slots", headers=auth_headers(UserRole.PROVIDER, email="viewer@example.com"))

    assert response.status_code == 200
    assert slot_id not in [slot["id"] for slot in response.json()]

import pytest
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import AvailabilitySlot, Booking, User, UserRole


def test_booking_slot_id_is_unique_at_the_database_level():
    db = SessionLocal()
    try:
        provider = User(email="provider@example.com", hashed_password="x", role=UserRole.PROVIDER)
        client = User(email="client@example.com", hashed_password="x", role=UserRole.CLIENT)
        db.add_all([provider, client])
        db.flush()

        slot = AvailabilitySlot(
            provider_id=provider.id,
            start_time="2026-01-01T09:00:00",
            end_time="2026-01-01T10:00:00",
        )
        db.add(slot)
        db.flush()

        db.add(Booking(slot_id=slot.id, client_id=client.id))
        db.commit()

        db.add(Booking(slot_id=slot.id, client_id=client.id))
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()

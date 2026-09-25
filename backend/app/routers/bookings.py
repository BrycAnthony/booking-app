from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, contains_eager

from app.database import get_db
from app.dependencies import require_client
from app.models import AvailabilitySlot, Booking, User
from app.schemas.booking import BookingCreate, BookingRead, BookingWithSlot

router = APIRouter(tags=["bookings"])


@router.post("/bookings", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_client),
) -> Booking:
    slot = db.get(AvailabilitySlot, booking_in.slot_id)
    if slot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found")

    booking = Booking(slot_id=booking_in.slot_id, client_id=current_user.id)
    db.add(booking)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Slot is already booked")
    db.refresh(booking)
    return booking


# Declared before any `/bookings/{booking_id}` GET route so "mine" isn't captured as an id.
@router.get("/bookings/mine", response_model=list[BookingWithSlot])
def list_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_client),
) -> list[Booking]:
    # join() lets us sort by the slot's start time; contains_eager() fills booking.slot
    # from that same join, so serializing each booking's slot doesn't fire one extra
    # query per booking (the N+1 problem).
    return (
        db.query(Booking)
        .join(Booking.slot)
        .options(contains_eager(Booking.slot))
        .filter(Booking.client_id == current_user.id)
        .order_by(AvailabilitySlot.start_time)
        .all()
    )


@router.delete("/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_client),
) -> None:
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.client_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only cancel your own bookings")
    db.delete(booking)
    db.commit()

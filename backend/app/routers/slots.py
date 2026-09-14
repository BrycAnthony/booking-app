from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_provider
from app.models import AvailabilitySlot, Booking, User
from app.schemas.slot import SlotCreate, SlotRead

router = APIRouter(tags=["slots"])


@router.post("/slots", response_model=SlotRead, status_code=status.HTTP_201_CREATED)
def create_slot(
    slot_in: SlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_provider),
) -> AvailabilitySlot:
    slot = AvailabilitySlot(
        provider_id=current_user.id,
        start_time=slot_in.start_time,
        end_time=slot_in.end_time,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.get("/slots", response_model=list[SlotRead])
def list_open_slots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AvailabilitySlot]:
    return (
        db.query(AvailabilitySlot)
        .outerjoin(Booking, Booking.slot_id == AvailabilitySlot.id)
        .filter(Booking.id.is_(None))
        .all()
    )

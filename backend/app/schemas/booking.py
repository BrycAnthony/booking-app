from pydantic import BaseModel

from app.schemas.slot import SlotRead


class BookingCreate(BaseModel):
    slot_id: int


class BookingRead(BaseModel):
    id: int
    slot_id: int
    client_id: int

    model_config = {"from_attributes": True}


class BookingWithSlot(BaseModel):
    """A booking plus its slot's times, so the client can display them without a second request."""

    id: int
    slot: SlotRead

    model_config = {"from_attributes": True}

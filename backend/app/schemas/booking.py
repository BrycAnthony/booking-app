from pydantic import BaseModel


class BookingCreate(BaseModel):
    slot_id: int


class BookingRead(BaseModel):
    id: int
    slot_id: int
    client_id: int

    model_config = {"from_attributes": True}

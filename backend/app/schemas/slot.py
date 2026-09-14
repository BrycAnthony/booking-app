from datetime import datetime

from pydantic import BaseModel


class SlotCreate(BaseModel):
    start_time: datetime
    end_time: datetime


class SlotRead(BaseModel):
    id: int
    provider_id: int
    start_time: datetime
    end_time: datetime

    model_config = {"from_attributes": True}

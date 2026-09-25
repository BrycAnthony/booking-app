from datetime import datetime

from pydantic import BaseModel, model_validator


class SlotCreate(BaseModel):
    start_time: datetime
    end_time: datetime

    # The database also enforces this with a CheckConstraint (see models/slot.py),
    # which is the real guarantee. Checking it here too means a bad request gets a
    # clean 422 with a readable message instead of an IntegrityError surfacing as a 500.
    @model_validator(mode="after")
    def end_after_start(self) -> "SlotCreate":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class SlotRead(BaseModel):
    id: int
    provider_id: int
    start_time: datetime
    end_time: datetime

    model_config = {"from_attributes": True}

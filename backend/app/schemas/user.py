from pydantic import BaseModel, EmailStr, Field

from app.models import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    # bcrypt only uses the first 72 bytes of a password; max_length avoids silent truncation confusion.
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole


class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: UserRole

    model_config = {"from_attributes": True}

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    admin = "admin"
    support = "support"
    user = "user"


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["johndoe"])
    email: EmailStr = Field(..., examples=["john@example.com"])
    role: UserRole = Field(..., examples=["support"])
    is_active: bool = Field(default=True)


class UserCreate(UserBase):
    """Body esperado en POST /users."""
    pass


class UserUpdate(UserBase):
    """Body esperado en PUT /users/{id}: reemplazo completo, todo obligatorio."""
    pass


class UserPatch(BaseModel):
    """Body esperado en PATCH /users/{id}: todos los campos opcionales."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
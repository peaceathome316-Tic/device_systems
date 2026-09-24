import re
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.user_schema import UserRole


def _validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    if " " in password:
        raise ValueError("La contraseña no puede contener espacios en blanco.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("La contraseña debe incluir al menos una letra mayúscula.")
    if not re.search(r"[a-z]", password):
        raise ValueError("La contraseña debe incluir al menos una letra minúscula.")
    if not re.search(r"[0-9]", password):
        raise ValueError("La contraseña debe incluir al menos un número.")
    return password


class UserRegister(BaseModel):
    """Body esperado en POST /auth/register."""

    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(..., min_length=3, max_length=50, examples=["johndoe"])
    email: EmailStr = Field(..., examples=["john@example.com"])
    password: str = Field(..., examples=["Secret123"])
    role: UserRole = Field(default=UserRole.user, examples=["user"])

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: str) -> str:
        return _validate_password_strength(value)


class UserLogin(BaseModel):
    """Body esperado en POST /auth/login."""

    email: EmailStr = Field(..., examples=["john@example.com"])
    password: str = Field(..., examples=["Secret123"])


class Token(BaseModel):
    """Respuesta de POST /auth/login."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Datos que se guardan dentro del payload del JWT."""

    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None


class AuthUserResponse(BaseModel):
    """Respuesta de GET /auth/me y de POST /auth/register: nunca incluye hashed_password."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
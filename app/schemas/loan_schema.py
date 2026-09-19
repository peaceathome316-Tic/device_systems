from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.device_schema import DeviceBasicInfo


class LoanStatus(str, Enum):
    active = "active"
    returned = "returned"
    overdue = "overdue"


class UserBasicInfo(BaseModel):
    """Versión reducida de un usuario, usada dentro de LoanDetailResponse."""
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class LoanBase(BaseModel):
    user_id: int = Field(..., examples=[1])
    device_id: int = Field(..., examples=[3])


class LoanCreate(LoanBase):
    """Body esperado en POST /loans."""
    pass


class LoanUpdate(BaseModel):
    """Body esperado para actualizar un préstamo (uso interno / administrativo)."""
    status: Optional[LoanStatus] = None
    return_date: Optional[datetime] = None


class LoanResponse(BaseModel):
    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: Optional[datetime] = None
    status: LoanStatus

    class Config:
        from_attributes = True


class LoanDetailResponse(BaseModel):
    """Respuesta con información relacionada de usuario y dispositivo (consultas con joins)."""
    loan_id: int
    status: LoanStatus
    loan_date: datetime
    return_date: Optional[datetime] = None
    user: UserBasicInfo
    device: DeviceBasicInfo

    class Config:
        from_attributes = True
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    laptop = "laptop"
    tablet = "tablet"
    proyector = "proyector"
    camara = "cámara"
    router = "router"
    monitor = "monitor"


class DeviceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Laptop Lenovo ThinkPad"])
    serial_number: str = Field(..., min_length=3, max_length=50, examples=["LEN-2024-001"])
    device_type: DeviceType = Field(..., examples=["laptop"])
    brand: Optional[str] = Field(None, examples=["Lenovo"])
    is_available: bool = Field(default=True)


class DeviceCreate(DeviceBase):
    """Body esperado en POST /devices."""
    pass


class DeviceUpdate(DeviceBase):
    """Body esperado en PUT /devices/{id}: reemplazo completo."""
    pass


class DevicePatch(BaseModel):
    """Body esperado en PATCH /devices/{id}: todos los campos opcionales."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    serial_number: Optional[str] = Field(None, min_length=3, max_length=50)
    device_type: Optional[DeviceType] = None
    brand: Optional[str] = None
    is_available: Optional[bool] = None


class DeviceResponse(DeviceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceBasicInfo(BaseModel):
    """Versión reducida, usada dentro de LoanDetailResponse."""
    id: int
    name: str
    serial_number: str
    device_type: DeviceType

    class Config:
        from_attributes = True
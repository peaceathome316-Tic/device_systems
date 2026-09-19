from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DevicePatch, DeviceUpdate


def get_devices(
    db: Session,
    device_type: Optional[str] = None,
    is_available: Optional[bool] = None,
    brand: Optional[str] = None,
    search: Optional[str] = None,
):
    query = db.query(Device)

    if device_type is not None:
        query = query.filter(Device.device_type == device_type)
    if is_available is not None:
        query = query.filter(Device.is_available == is_available)
    if brand is not None:
        query = query.filter(Device.brand.ilike(f"%{brand}%"))
    if search is not None:
        query = query.filter(
            or_(
                Device.name.ilike(f"%{search}%"),
                Device.serial_number.ilike(f"%{search}%"),
            )
        )

    return query.all()


def get_device_by_id(db: Session, device_id: int) -> Device:
    device = db.query(Device).filter(Device.id == device_id).first()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo con ID {device_id} no encontrado.",
        )
    return device


def get_device_by_serial(db: Session, serial_number: str) -> Optional[Device]:
    return db.query(Device).filter(Device.serial_number == serial_number).first()


def create_device(db: Session, device_data: DeviceCreate) -> Device:
    if get_device_by_serial(db, device_data.serial_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un dispositivo registrado con ese número de serie.",
        )
    new_device = Device(**device_data.model_dump())
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device


def replace_device(db: Session, device_id: int, device_data: DeviceUpdate) -> Device:
    device = get_device_by_id(db, device_id)

    duplicate = get_device_by_serial(db, device_data.serial_number)
    if duplicate and duplicate.id != device_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un dispositivo registrado con ese número de serie.",
        )

    for field, value in device_data.model_dump().items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)
    return device


def update_device_partial(db: Session, device_id: int, patch_data: DevicePatch) -> Device:
    device = get_device_by_id(db, device_id)

    update_dict = patch_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar.",
        )

    if "serial_number" in update_dict:
        duplicate = get_device_by_serial(db, update_dict["serial_number"])
        if duplicate and duplicate.id != device_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un dispositivo registrado con ese número de serie.",
            )

    for field, value in update_dict.items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device_id: int) -> None:
    device = get_device_by_id(db, device_id)
    db.delete(device)
    db.commit()
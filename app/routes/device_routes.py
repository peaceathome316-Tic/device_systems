from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.schemas.device_schema import (
    DeviceCreate,
    DevicePatch,
    DeviceResponse,
    DeviceType,
    DeviceUpdate,
)
from app.schemas.loan_schema import LoanDetailResponse
from app.services import device_service, loan_service

router = APIRouter(prefix="/devices", tags=["Devices"])


# --- CREAR DISPOSITIVO (POST) ---
@router.post(
    "/",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo dispositivo",
    description="Crea un nuevo dispositivo tecnológico disponible para préstamo. Valida que el número de serie no esté duplicado.",
    response_description="Dispositivo creado exitosamente.",
)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    return device_service.create_device(db, device)


# --- LISTAR / FILTRAR DISPOSITIVOS (GET) ---
@router.get(
    "/",
    response_model=List[DeviceResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar dispositivos",
    description="Devuelve los dispositivos registrados, con filtros opcionales por tipo, disponibilidad, marca o texto de búsqueda.",
    response_description="Lista de dispositivos.",
)
def list_devices(
    db: Session = Depends(get_db),
    device_type: Optional[DeviceType] = Query(None, description="Filtrar por tipo de dispositivo"),
    is_available: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    brand: Optional[str] = Query(None, description="Filtrar por marca (coincidencia parcial)"),
    search: Optional[str] = Query(None, description="Buscar por nombre o número de serie"),
):
    return device_service.get_devices(
        db,
        device_type=device_type,
        is_available=is_available,
        brand=brand,
        search=search,
    )


# --- CONSULTAR DISPOSITIVO POR ID (GET) ---
@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar dispositivo por ID",
    description="Devuelve un dispositivo específico según su ID.",
    response_description="Dispositivo encontrado.",
)
def get_device(device_id: int, db: Session = Depends(get_db)):
    return device_service.get_device_by_id(db, device_id)


# --- CONSULTA CON JOIN: historial de préstamos de un dispositivo (Fase 10) ---
@router.get(
    "/{device_id}/loans",
    response_model=List[LoanDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar historial de préstamos de un dispositivo",
    description="Devuelve todos los préstamos (históricos y activos) asociados a un dispositivo, con la información del usuario incluida.",
    response_description="Lista de préstamos del dispositivo.",
)
def get_device_loans(device_id: int, db: Session = Depends(get_db)):
    return loan_service.get_device_loans_details(db, device_id)


# --- ACTUALIZACIÓN COMPLETA (PUT) ---
@router.put(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar dispositivo completo",
    description="Reemplaza todos los campos de un dispositivo existente.",
    response_description="Dispositivo actualizado.",
)
def replace_device(device_id: int, device_data: DeviceUpdate, db: Session = Depends(get_db)):
    return device_service.replace_device(db, device_id, device_data)


# --- ACTUALIZACIÓN PARCIAL (PATCH) ---
@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar dispositivo parcialmente",
    description="Actualiza solo los campos enviados por el cliente.",
    response_description="Dispositivo actualizado parcialmente.",
)
def update_device(device_id: int, device_data: DevicePatch, db: Session = Depends(get_db)):
    return device_service.update_device_partial(db, device_id, device_data)


# --- ELIMINAR DISPOSITIVO (DELETE) ---
@router.delete(
    "/{device_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar dispositivo",
    description="Elimina un dispositivo existente.",
    response_description="Confirmación de eliminación.",
)
def delete_device(device_id: int, db: Session = Depends(get_db)):
    device_service.delete_device(db, device_id)
    return {"detail": f"Dispositivo con ID {device_id} eliminado correctamente."}
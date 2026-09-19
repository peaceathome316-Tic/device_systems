from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.schemas.device_schema import DeviceType
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse, LoanStatus
from app.services import loan_service

router = APIRouter(prefix="/loans", tags=["Loans"])


# --- CREAR PRÉSTAMO (POST) ---
@router.post(
    "/",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo préstamo",
    description=(
        "Crea un préstamo asociando un usuario a un dispositivo. Valida que el usuario y el "
        "dispositivo existan, y que el dispositivo esté disponible. Marca el dispositivo como no disponible."
    ),
    response_description="Préstamo creado exitosamente.",
)
def create_loan(loan: LoanCreate, db: Session = Depends(get_db)):
    return loan_service.create_loan(db, loan)


# --- LISTAR / FILTRAR PRÉSTAMOS (GET) ---
@router.get(
    "/",
    response_model=List[LoanResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar préstamos",
    description="Devuelve los préstamos registrados, con filtros opcionales por estado, usuario o dispositivo.",
    response_description="Lista de préstamos.",
)
def list_loans(
    db: Session = Depends(get_db),
    status_filter: Optional[LoanStatus] = Query(None, alias="status", description="Filtrar por estado del préstamo"),
    user_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    device_id: Optional[int] = Query(None, description="Filtrar por ID de dispositivo"),
):
    return loan_service.get_loans(db, status_filter=status_filter, user_id=user_id, device_id=device_id)


# --- CONSULTA CON JOINS: préstamos con datos de usuario y dispositivo (Fase 10) ---
@router.get(
    "/details",
    response_model=List[LoanDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar préstamos con información relacionada",
    description=(
        "Devuelve los préstamos junto con los datos básicos del usuario y del dispositivo, "
        "usando joins. Permite filtrar por estado, correo del usuario o tipo de dispositivo."
    ),
    response_description="Lista de préstamos con información relacionada.",
)
def list_loans_details(
    db: Session = Depends(get_db),
    status_filter: Optional[LoanStatus] = Query(None, alias="status", description="Filtrar por estado del préstamo"),
    user_email: Optional[str] = Query(None, description="Filtrar por correo del usuario (coincidencia parcial)"),
    device_type: Optional[DeviceType] = Query(None, description="Filtrar por tipo de dispositivo"),
):
    return loan_service.get_loans_details(
        db,
        status_filter=status_filter,
        user_email=user_email,
        device_type=device_type,
    )


# --- CONSULTAR PRÉSTAMO POR ID (GET) ---
@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar préstamo por ID",
    description="Devuelve un préstamo específico según su ID.",
    response_description="Préstamo encontrado.",
)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    return loan_service.get_loan_by_id(db, loan_id)


# --- DEVOLVER DISPOSITIVO (PATCH) ---
@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    status_code=status.HTTP_200_OK,
    summary="Registrar la devolución de un préstamo",
    description=(
        "Marca un préstamo como devuelto, asigna la fecha de devolución y vuelve a poner "
        "el dispositivo asociado como disponible. Falla si el préstamo ya fue devuelto."
    ),
    response_description="Préstamo marcado como devuelto.",
)
def return_loan(loan_id: int, db: Session = Depends(get_db)):
    return loan_service.return_loan(db, loan_id)
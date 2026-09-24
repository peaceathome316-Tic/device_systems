from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.dependencies.auth_dependency import get_current_active_user, require_admin_or_support
from app.dependencies.database_dependency import get_db
from app.middlewares.rate_limiter import limiter
from app.models.user_model import User
from app.schemas.device_schema import DeviceType
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse, LoanStatus
from app.services import loan_service

router = APIRouter(prefix="/loans", tags=["Loans"])


# --- CREAR PRÉSTAMO (POST) --- Requiere estar autenticado
@router.post(
    "/",
    response_model=LoanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo préstamo",
    description=(
        "Crea un préstamo asociando un usuario a un dispositivo. Requiere estar autenticado. "
        "Valida que el usuario y el dispositivo existan, y que el dispositivo esté disponible. "
        "Límite: 10 solicitudes por minuto."
    ),
    response_description="Préstamo creado exitosamente.",
)
@limiter.limit("10/minute")
def create_loan(
    request: Request,
    loan: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return loan_service.create_loan(db, loan)


# --- LISTAR / FILTRAR PRÉSTAMOS (GET) --- Requiere estar autenticado
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
    current_user: User = Depends(get_current_active_user),
):
    return loan_service.get_loans(db, status_filter=status_filter, user_id=user_id, device_id=device_id)


# --- CONSULTA CON JOINS --- Requiere rol admin o support
@router.get(
    "/details",
    response_model=List[LoanDetailResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar préstamos con información relacionada",
    description=(
        "Devuelve los préstamos junto con los datos básicos del usuario y del dispositivo, "
        "usando joins. Requiere rol admin o support."
    ),
    response_description="Lista de préstamos con información relacionada.",
)
def list_loans_details(
    db: Session = Depends(get_db),
    status_filter: Optional[LoanStatus] = Query(None, alias="status", description="Filtrar por estado del préstamo"),
    user_email: Optional[str] = Query(None, description="Filtrar por correo del usuario (coincidencia parcial)"),
    device_type: Optional[DeviceType] = Query(None, description="Filtrar por tipo de dispositivo"),
    current_user: User = Depends(require_admin_or_support),
):
    return loan_service.get_loans_details(
        db,
        status_filter=status_filter,
        user_email=user_email,
        device_type=device_type,
    )


# --- CONSULTAR PRÉSTAMO POR ID (GET) --- Requiere estar autenticado
@router.get(
    "/{loan_id}",
    response_model=LoanResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar préstamo por ID",
    description="Devuelve un préstamo específico según su ID.",
    response_description="Préstamo encontrado.",
)
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return loan_service.get_loan_by_id(db, loan_id)


# --- DEVOLVER DISPOSITIVO (PATCH) --- Requiere rol admin o support
@router.patch(
    "/{loan_id}/return",
    response_model=LoanResponse,
    status_code=status.HTTP_200_OK,
    summary="Registrar la devolución de un préstamo",
    description=(
        "Marca un préstamo como devuelto y libera el dispositivo asociado. "
        "Requiere rol admin o support. Falla si el préstamo ya fue devuelto."
    ),
    response_description="Préstamo marcado como devuelto.",
)
def return_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_support),
):
    return loan_service.return_loan(db, loan_id)
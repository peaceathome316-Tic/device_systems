from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.device_schema import DeviceBasicInfo
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, UserBasicInfo


def _to_detail_response(loan: Loan) -> LoanDetailResponse:
    """Convierte un Loan (con sus relaciones cargadas) al schema con datos combinados."""
    return LoanDetailResponse(
        loan_id=loan.id,
        status=loan.status,
        loan_date=loan.loan_date,
        return_date=loan.return_date,
        user=UserBasicInfo.model_validate(loan.user),
        device=DeviceBasicInfo.model_validate(loan.device),
    )


def get_loan_by_id(db: Session, loan_id: int) -> Loan:
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if loan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Préstamo con ID {loan_id} no encontrado.",
        )
    return loan


def get_loans(db: Session, status_filter: Optional[str] = None, user_id: Optional[int] = None, device_id: Optional[int] = None):
    query = db.query(Loan)
    if status_filter is not None:
        query = query.filter(Loan.status == status_filter)
    if user_id is not None:
        query = query.filter(Loan.user_id == user_id)
    if device_id is not None:
        query = query.filter(Loan.device_id == device_id)
    return query.all()


def create_loan(db: Session, loan_data: LoanCreate) -> Loan:
    # Validar que el usuario exista
    user = db.query(User).filter(User.id == loan_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {loan_data.user_id} no encontrado.",
        )

    # Validar que el dispositivo exista
    device = db.query(Device).filter(Device.id == loan_data.device_id).first()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo con ID {loan_data.device_id} no encontrado.",
        )

    # Validar que el dispositivo esté disponible
    if not device.is_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El dispositivo con ID {device.id} no está disponible para préstamo.",
        )

    new_loan = Loan(
        user_id=user.id,
        device_id=device.id,
        loan_date=datetime.utcnow(),
        status="active",
    )
    device.is_available = False

    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return new_loan


def return_loan(db: Session, loan_id: int) -> Loan:
    loan = get_loan_by_id(db, loan_id)

    if loan.status == "returned":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El préstamo con ID {loan_id} ya fue devuelto anteriormente.",
        )

    loan.status = "returned"
    loan.return_date = datetime.utcnow()

    device = db.query(Device).filter(Device.id == loan.device_id).first()
    if device is not None:
        device.is_available = True

    db.commit()
    db.refresh(loan)
    return loan


# --- Consultas con joins y filtros (Fase 10) ---

def get_loans_details(
    db: Session,
    status_filter: Optional[str] = None,
    user_email: Optional[str] = None,
    device_type: Optional[str] = None,
):
    query = (
        db.query(Loan)
        .join(User, Loan.user_id == User.id)
        .join(Device, Loan.device_id == Device.id)
        .options(joinedload(Loan.user), joinedload(Loan.device))
    )

    if status_filter is not None:
        query = query.filter(Loan.status == status_filter)
    if user_email is not None:
        query = query.filter(User.email.ilike(f"%{user_email}%"))
    if device_type is not None:
        query = query.filter(Device.device_type == device_type)

    loans = query.all()
    return [_to_detail_response(loan) for loan in loans]


def get_user_loans_details(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado.",
        )
    loans = (
        db.query(Loan)
        .filter(Loan.user_id == user_id)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .all()
    )
    return [_to_detail_response(loan) for loan in loans]


def get_device_loans_details(db: Session, device_id: int):
    device = db.query(Device).filter(Device.id == device_id).first()
    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo con ID {device_id} no encontrado.",
        )
    loans = (
        db.query(Loan)
        .filter(Loan.device_id == device_id)
        .options(joinedload(Loan.user), joinedload(Loan.device))
        .all()
    )
    return [_to_detail_response(loan) for loan in loans]
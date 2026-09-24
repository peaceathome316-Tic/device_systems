from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import auth_service
from app.dependencies.auth_dependency import get_current_active_user
from app.dependencies.database_dependency import get_db
from app.middlewares.rate_limiter import limiter
from app.models.user_model import User
from app.schemas.auth_schema import AuthUserResponse, Token, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=AuthUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
    description=(
        "Crea un usuario con contraseña segura (mínimo 8 caracteres, con mayúscula, minúscula "
        "y número, sin espacios). La contraseña se guarda como hash, nunca en texto plano. "
        "Límite: 3 solicitudes por minuto."
    ),
    response_description="Usuario registrado exitosamente (sin la contraseña).",
)
@limiter.limit("3/minute")
def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    return auth_service.register_user(db, user_data)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    description=(
        "Autentica al usuario con su correo (campo 'username' del formulario) y contraseña, "
        "y devuelve un token JWT de acceso. Límite: 5 solicitudes por minuto."
    ),
    response_description="Token de acceso generado.",
)
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # form_data.username se usa como el correo electrónico del usuario
    return auth_service.login(db, email=form_data.username, password=form_data.password)


@router.get(
    "/me",
    response_model=AuthUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar el usuario autenticado",
    description="Devuelve los datos del usuario dueño del token enviado en la cabecera Authorization.",
    response_description="Datos del usuario autenticado (sin la contraseña).",
)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user
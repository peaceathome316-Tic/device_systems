from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.dependencies.database_dependency import get_db
from app.models.user_model import User

# tokenUrl le indica a Swagger dónde está el endpoint de login,
# para que el botón "Authorize" funcione automáticamente.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependencia base: valida el token JWT y devuelve el usuario autenticado.
    Responde 401 si el token es inválido, expiró, o el usuario ya no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Además de autenticado, exige que el usuario esté activo."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo.",
        )
    return current_user


def require_roles(*allowed_roles: str):
    """
    Fábrica de dependencias: crea una dependencia que exige que el usuario
    autenticado tenga uno de los roles indicados. Uso:
        Depends(require_roles("admin"))
        Depends(require_roles("admin", "support"))
    """

    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para realizar esta acción.",
            )
        return current_user

    return role_checker


# Atajos usados frecuentemente en las rutas
require_admin = require_roles("admin")
require_admin_or_support = require_roles("admin", "support")
from fastapi import HTTPException, status, Header
from typing import Optional

from app.services.user_service import find_user


def get_user_or_404(user_id: int) -> dict:
    """
    Dependencia reutilizable: busca un usuario por ID.
    Si no existe, lanza automáticamente un 404 antes de llegar al endpoint.
    Úsala en las rutas así: user: dict = Depends(get_user_or_404)
    """
    user = find_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado.",
        )
    return user


def verify_api_key(x_api_key: Optional[str] = Header(default=None)) -> str:
    """
    Dependencia opcional: simula autenticación básica mediante una cabecera
    personalizada 'X-API-Key'. No se aplica por defecto a ninguna ruta;
    agrégala con Depends(verify_api_key) en el endpoint que quieras proteger.
    """
    if x_api_key is None or x_api_key != "device-systems-secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas o cabecera X-API-Key ausente.",
        )
    return x_api_key
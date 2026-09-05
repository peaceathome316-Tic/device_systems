from fastapi import HTTPException, status
from typing import List, Optional

from app.data.users_db import db_users, get_next_id


def list_users(role: Optional[str] = None, is_active: Optional[bool] = None) -> List[dict]:
    result = db_users
    if role is not None:
        result = [u for u in result if u["role"] == role]
    if is_active is not None:
        result = [u for u in result if u["is_active"] == is_active]
    return result


def find_user(user_id: int) -> Optional[dict]:
    return next((u for u in db_users if u["id"] == user_id), None)


def email_taken(email: str, exclude_id: Optional[int] = None) -> bool:
    return any(u["email"] == email and u["id"] != exclude_id for u in db_users)


def create_user(user_data: dict) -> dict:
    if email_taken(user_data["email"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado en device_systems.",
        )
    user_data["id"] = get_next_id()
    db_users.append(user_data)
    return user_data


def replace_user(user_id: int, new_data: dict) -> dict:
    """Reemplazo completo (PUT). Conserva la password original si existía."""
    current = find_user(user_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado.",
        )
    if email_taken(new_data["email"], exclude_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado en device_systems.",
        )

    new_data = new_data.copy()
    new_data["id"] = user_id
    if "password" in current:
        new_data["password"] = current["password"]

    index = db_users.index(current)
    db_users[index] = new_data
    return new_data


def update_user_partial(user_id: int, update_data: dict) -> dict:
    """Actualización parcial (PATCH)."""
    current = find_user(user_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado.",
        )
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se enviaron campos para actualizar.",
        )
    if "email" in update_data and email_taken(update_data["email"], exclude_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado en device_systems.",
        )

    current.update(update_data)
    return current


def delete_user(user_id: int) -> None:
    current = find_user(user_id)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {user_id} no encontrado.",
        )
    db_users.remove(current)
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies.database_dependency import get_db
from app.schemas.user_schema import UserCreate, UserPatch, UserResponse, UserRole, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


# --- CREAR USUARIO (POST) ---
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario",
    description="Registra un nuevo usuario en la base de datos de device_systems.",
    response_description="Usuario creado exitosamente.",
)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)


# --- LISTAR / FILTRAR / ORDENAR USUARIOS (GET) ---
@router.get(
    "/",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description="Devuelve los usuarios almacenados en la base de datos, con filtros por rol/estado y ordenamiento opcional.",
    response_description="Lista de usuarios.",
)
def list_users(
    db: Session = Depends(get_db),
    role: Optional[UserRole] = Query(None, description="Filtrar por rol (admin, support, user)"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    order_by: Optional[str] = Query(None, description="Ordenar por 'name' o 'created_at'"),
):
    return user_service.get_users(db, role=role, is_active=is_active, order_by=order_by)


# --- CONSULTAR USUARIO POR ID (GET) ---
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar usuario por ID",
    description="Busca un usuario específico en la base de datos.",
    response_description="Usuario encontrado.",
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user_by_id(db, user_id)


# --- ACTUALIZACIÓN COMPLETA (PUT) ---
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario completo",
    description="Reemplaza todos los campos de un usuario existente en la base de datos.",
    response_description="Usuario actualizado.",
)
def replace_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    return user_service.replace_user(db, user_id, user_data)


# --- ACTUALIZACIÓN PARCIAL (PATCH) ---
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario parcialmente",
    description="Actualiza solo los campos enviados por el cliente. Si no se envía ningún campo, responde 400.",
    response_description="Usuario actualizado parcialmente.",
)
def update_user(user_id: int, user_data: UserPatch, db: Session = Depends(get_db)):
    return user_service.update_user_partial(db, user_id, user_data)


# --- ELIMINAR USUARIO (DELETE) ---
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar usuario",
    description="Elimina un usuario existente de la base de datos.",
    response_description="Confirmación de eliminación.",
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_service.delete_user(db, user_id)
    return {"detail": f"Usuario con ID {user_id} eliminado correctamente."}
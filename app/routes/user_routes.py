from fastapi import APIRouter, status, Query, Depends
from typing import List, Optional

from app.schemas.user_schema import UserCreate, UserUpdate, UserBase, UserResponse, UserRole
from app.dependencies.user_dependencies import get_user_or_404
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


# --- CREAR USUARIO (POST) ---
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo usuario",
    description="Registra un nuevo usuario en device_systems. Valida que el correo no esté duplicado.",
    response_description="Usuario creado exitosamente.",
)
def create_user(user: UserCreate):
    return user_service.create_user(user.model_dump())


# --- LISTAR / FILTRAR USUARIOS (GET) ---
@router.get(
    "/",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar usuarios",
    description="Devuelve la lista de usuarios, con filtros opcionales por rol y estado activo.",
    response_description="Lista de usuarios.",
)
def get_users(
    role: Optional[UserRole] = Query(None, description="Filtrar por rol (admin, operator, user)"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
):
    return user_service.list_users(role=role, is_active=is_active)


# --- CONSULTAR USUARIO POR ID (GET) ---
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar usuario por ID",
    description="Devuelve un usuario específico según su ID.",
    response_description="Usuario encontrado.",
)
def get_user_by_id(user: dict = Depends(get_user_or_404)):
    return user


# --- ACTUALIZACIÓN COMPLETA (PUT) — Fase 3 ---
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario completo",
    description="Reemplaza toda la información de un usuario existente. Requiere todos los campos.",
    response_description="Usuario actualizado.",
)
def replace_user(
    user_id: int,
    user_data: UserBase,
    _: dict = Depends(get_user_or_404),
):
    return user_service.replace_user(user_id, user_data.model_dump())


# --- ACTUALIZACIÓN PARCIAL (PATCH) — Fase 3 ---
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar usuario parcialmente",
    description="Actualiza solo los campos enviados por el cliente. Si no se envía ningún campo, responde 400.",
    response_description="Usuario actualizado parcialmente.",
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    _: dict = Depends(get_user_or_404),
):
    update_dict = user_data.model_dump(exclude_unset=True)
    return user_service.update_user_partial(user_id, update_dict)


# --- ELIMINAR USUARIO (DELETE) — Fase 4 ---
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar usuario",
    description="Elimina un usuario existente por su ID.",
    response_description="Confirmación de eliminación.",
)
def delete_user(
    user_id: int,
    _: dict = Depends(get_user_or_404),
):
    user_service.delete_user(user_id)
    return {"detail": f"Usuario con ID {user_id} eliminado correctamente."}
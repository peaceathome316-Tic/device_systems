from fastapi import APIRouter, HTTPException, status, Query, Response
from typing import List, Optional
from app.schemas.user_schema import UserCreate, UserResponse, UserRole

router = APIRouter(prefix="/users", tags=["Users"])

# Base de datos simulada en memoria con un usuario de prueba
db_users = [
    {
        "id": 1,
        "name": "cristian jaramillo",
        "email": "cristian@device.com",
        "role": "admin",
        "is_active": True
    }
]
id_counter = 2

# Función auxiliar para inyectar cabeceras personalizadas (Fase 5)
def set_custom_headers(response: Response):
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "1.0"

# --- FASE 4: REGISTRAR USUARIO (POST) ---
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, response: Response):
    global id_counter
    
    # Validar correo duplicado
    if any(u["email"] == user.email for u in db_users):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado en device_systems."
        )
    
    user_dict = user.model_dump()
    user_dict["id"] = id_counter
    db_users.append(user_dict)
    id_counter += 1
    
    set_custom_headers(response)
    return user_dict

# --- FASE 3: OBTENER USUARIOS Y FILTRAR (GET) ---
@router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def get_users(
    response: Response,
    role: Optional[UserRole] = Query(None, description="Filtrar por rol (admin, support, user)"),
    is_active: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo")
):
    filtered_users = db_users
    
    # Filtro por rol (?role=admin)
    if role is not None:
        filtered_users = [u for u in filtered_users if u["role"] == role]
        
    # Filtro por estado activo (?is_active=true)
    if is_active is not None:
        filtered_users = [u for u in filtered_users if u["is_active"] == is_active]
        
    set_custom_headers(response)
    return filtered_users

# --- FASE 3: OBTENER USUARIO POR ID (GET /{user_id}) ---
@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, response: Response):
    for u in db_users:
        if u["id"] == user_id:
            set_custom_headers(response)
            return u
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Usuario con ID {user_id} no encontrado."
    )
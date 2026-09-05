# Simulación de base de datos en memoria (Fase 2)

db_users = [
    {
        "id": 1,
        "username": "cristian jaramillo",
        "email": "cristian@device.com",
        "role": "admin",
        "is_active": True,
        "password": "changeme123",
    }
]

_id_counter = 2


def get_next_id() -> int:
    """Genera y reserva el siguiente ID disponible."""
    global _id_counter
    current = _id_counter
    _id_counter += 1
    return current
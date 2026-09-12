from app.database.connection import SessionLocal


def get_db():
    """
    Dependencia reutilizable con Depends(): entrega una sesión de base
    de datos a la ruta y la cierra automáticamente al terminar,
    incluso si ocurre un error durante la petición.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
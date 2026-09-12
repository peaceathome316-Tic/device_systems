from fastapi import FastAPI, Request

from app.database.connection import Base, engine
from app.routes.user_routes import router as user_router

# Crea las tablas en la base de datos si todavía no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="device_systems API",
    description="API REST para la gestión de usuarios de device_systems, con persistencia en base de datos mediante SQLAlchemy.",
    version="3.0.0",
)


@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "3.0"
    return response


# Registrar el enrutador de usuarios
app.include_router(user_router)


@app.get("/", tags=["Health Check"])
def root():
    return {"message": "API device_systems ejecutándose correctamente."}
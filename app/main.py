from fastapi import FastAPI, Request
from app.routes.user_routes import router as user_router

app = FastAPI(
    title="device_systems API",
    description="API REST para la gestión de usuarios del sistema device_systems",
    version="2.0.0",
)


@app.middleware("http")
async def agregar_cabeceras_personalizadas(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-App-Name"] = "device_systems"
    response.headers["X-API-Version"] = "2.0"
    return response


# Registrar el enrutador de usuarios
app.include_router(user_router)


@app.get("/", tags=["Health Check"])
def root():
    return {"message": "API device_systems ejecutándose correctamente."}
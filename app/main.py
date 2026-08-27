from fastapi import FastAPI
from app.routes.user_routes import router as user_router

app = FastAPI(
    title="device_systems API",
    description="Mi API REST para administrar usuarios de mi sistema device_systems",
    version="1.0.0"
)

# Registrar el enrutador de usuarios
app.include_router(user_router)

@app.get("/", tags=["Health Check"])
def root():
    return {"message": "API device_systems ejecutándose correctamente."}
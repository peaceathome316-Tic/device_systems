from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.auth.auth_routes import router as auth_router
from app.database.connection import Base, engine
from app.middlewares.rate_limiter import limiter
from app.middlewares.request_middleware import register_request_middleware
from app.routes.device_routes import router as device_router
from app.routes.loan_routes import router as loan_router
from app.routes.user_routes import router as user_router

# Crea las tablas en la base de datos si todavía no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="device_systems API",
    description="API REST segura para gestión de usuarios, dispositivos y préstamos",
    version="3.0.0",
)

# --- Rate limiting (Fase 11) ---
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# --- CORS (Fase 9) ---
# Para desarrollo, solo se permiten estos orígenes locales de frontend.
# No se recomienda usar "*" cuando allow_credentials=True: el estándar CORS
# prohíbe combinar un origen comodín con credenciales (cookies, cabeceras de
# autorización), porque cualquier sitio web podría hacer peticiones autenticadas
# a la API en nombre del usuario. Por eso se debe listar explícitamente cada
# dominio de confianza, tanto en desarrollo como en producción.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Middleware personalizado (Fase 10) ---
register_request_middleware(app)

# --- Routers ---
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(device_router)
app.include_router(loan_router)


@app.get("/", tags=["Health Check"])
def root():
    return {"message": "API device_systems ejecutándose correctamente."}
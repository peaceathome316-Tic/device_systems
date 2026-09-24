import time
import uuid

from starlette.requests import Request


def register_request_middleware(app):
    """
    Registra un middleware que:
    - Mide el tiempo de respuesta de cada petición.
    - Agrega las cabeceras X-App-Name, X-Process-Time y X-Request-ID.
    - Propaga un X-Request-ID si el cliente ya envió uno, o genera uno nuevo.
    - Registra en consola método, ruta y código de estado de cada petición.
    """

    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:8])
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-App-Name"] = "device_systems"
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-Request-ID"] = request_id

        print(
            f"[{request_id}] {request.method} {request.url.path} "
            f"-> {response.status_code} ({process_time:.4f}s)"
        )

        return response
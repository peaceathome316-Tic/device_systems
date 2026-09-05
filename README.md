

evidencias:
![alt text](<images/Captura de pantalla 2026-08-22 082610.png>)
![alt text](<images/Captura de pantalla 2026-08-26 194509.png>)
![alt text](<images/Captura de pantalla 2026-08-26 194621.png>)

# device_systems

API REST para la gestión de usuarios del sistema **device_systems**, construida con FastAPI. Evoluciona la versión anterior (solo GET/POST) hacia una API completa: CRUD total sobre el recurso `users`, manejo profesional de errores, códigos de estado HTTP correctos, documentación automática con Swagger/OpenAPI y reutilización de lógica mediante Dependency Injection.

## Tecnologías utilizadas

- Python 3.11+
- FastAPI
- Uvicorn (servidor ASGI)
- Pydantic v2 (validación de datos)
- Git y GitHub (control de versiones)

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── main.py                     # Punto de entrada: crea la app, registra rutas y middleware
│   ├── routes/
│   │   └── user_routes.py          # Definición de todos los endpoints de /users
│   ├── schemas/
│   │   └── user_schema.py          # Modelos Pydantic de entrada y salida
│   ├── services/
│   │   └── user_service.py         # Lógica de negocio (crear, buscar, actualizar, borrar)
│   ├── dependencies/
│   │   └── user_dependencies.py    # Funciones reutilizables con Depends()
│   └── data/
│       └── users_db.py             # Simulación de base de datos en memoria
├── requirements.txt
├── .gitignore
└── README.md
```

Cada capa tiene una única responsabilidad:
- **routes**: recibe la petición HTTP y delega en `services`. No contiene lógica de negocio.
- **schemas**: valida lo que entra y define la forma de lo que sale.
- **services**: contiene las reglas del negocio (duplicados de correo, existencia del usuario, etc.).
- **dependencies**: lógica reutilizable inyectada con `Depends()` en varias rutas a la vez.
- **data**: reemplaza a una base de datos real; toda la información vive en memoria mientras el servidor está corriendo.

## Instalación

```bash
git clone <URL-de-tu-repositorio>
cd device_systems

python -m venv venv
source venv/Scripts/activate      # En Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
```

## Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`.

- Documentación interactiva (Swagger UI): `http://127.0.0.1:8000/docs`
- Documentación alternativa (ReDoc): `http://127.0.0.1:8000/redoc`

## Tabla de endpoints

| Operación | Método | Ruta | Código éxito | Código error |
|---|---|---|---|---|
| Listar usuarios (con filtros opcionales `role`, `is_active`) | GET | `/users` | 200 OK | — |
| Consultar usuario por ID | GET | `/users/{user_id}` | 200 OK | 404 Not Found |
| Crear usuario | POST | `/users` | 201 Created | 400 (correo duplicado) / 422 (datos inválidos) |
| Actualizar usuario completo | PUT | `/users/{user_id}` | 200 OK | 404 Not Found / 400 (correo duplicado) |
| Actualizar usuario parcial | PATCH | `/users/{user_id}` | 200 OK | 404 Not Found / 400 (sin campos enviados) |
| Eliminar usuario | DELETE | `/users/{user_id}` | 200 OK | 404 Not Found |

## Ejemplos de peticiones y respuestas

### Crear usuario — `POST /users`

Request:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "role": "operator",
  "is_active": true,
  "password": "secret123"
}
```

Respuesta `201 Created`:
```json
{
  "id": 2,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "operator",
  "is_active": true
}
```

### Actualización parcial — `PATCH /users/{user_id}`

Request:
```json
{
  "role": "support"
}
```

Respuesta `200 OK`: el usuario completo con solo el campo `role` modificado.

### PATCH sin campos — error controlado

Request:
```json
{}
```

Respuesta `400 Bad Request`:
```json
{
  "detail": "No se enviaron campos para actualizar."
}
```

### Usuario no encontrado — error controlado

Respuesta `404 Not Found`:
```json
{
  "detail": "Usuario con ID 999 no encontrado."
}
```

### Correo duplicado — error controlado

Respuesta `400 Bad Request`:
```json
{
  "detail": "El correo electrónico ya está registrado en device_systems."
}
```

## Códigos de estado usados

| Código | Significado en esta API |
|---|---|
| 200 OK | Operación exitosa (GET, PUT, PATCH, DELETE) |
| 201 Created | Usuario creado exitosamente |
| 400 Bad Request | Correo duplicado o PATCH sin campos |
| 404 Not Found | El usuario solicitado no existe |
| 422 Unprocessable Entity | Datos de entrada inválidos (validación de Pydantic) |

## Uso de Dependency Injection (`Depends()`)

La función `get_user_or_404` (en `app/dependencies/user_dependencies.py`) centraliza la búsqueda de un usuario por ID:

```python
def get_user_or_404(user_id: int) -> dict:
    user = find_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {user_id} no encontrado.")
    return user
```

Se inyecta en `GET /users/{id}`, `PUT /users/{id}`, `PATCH /users/{id}` y `DELETE /users/{id}` mediante `Depends(get_user_or_404)`. Esto evita repetir el mismo bloque de "buscar usuario o lanzar 404" en cada endpoint: la validación ocurre antes de que el código de la ruta se ejecute, y si el usuario no existe, la petición nunca llega a la lógica del endpoint.

## Manejo de errores implementado

Todos los errores previsibles se controlan con `HTTPException`, devolviendo un JSON consistente `{"detail": "..."}`:

- **Usuario no encontrado** → 404, vía la dependencia `get_user_or_404`.
- **Correo electrónico duplicado** → 400, validado en `user_service.py` tanto en creación (`POST`) como en reemplazo (`PUT`) y actualización parcial (`PATCH`).
- **Actualización sin datos (PATCH vacío)** → 400, validado en `user_service.update_user_partial`.
- **Datos inválidos** (email mal formado, campos faltantes, tipos incorrectos) → 422, generado automáticamente por la validación de Pydantic antes de que la petición llegue al endpoint.

Además, un middleware en `main.py` agrega las cabeceras `X-App-Name` y `X-API-Version` a **todas** las respuestas, incluidas las de error.

## Flujo de ramas Git usado en este proyecto

- **`main`**: contiene únicamente la versión inicial del proyecto (configuración base, GET y POST). No recibe cambios de esta actividad.
- **`develop`**: rama de integración creada a partir de `main`.
- **`feature`**: rama donde se desarrolló el CRUD completo de esta actividad (PUT, PATCH, DELETE, reestructuración en capas, Dependency Injection). Se fusionó hacia `develop` una vez probada.

## Evidencia de pruebas

> Reemplaza esta sección con tus propias capturas.

- [ ] Captura de Swagger UI (`/docs`) mostrando todos los endpoints.
- [ ] Captura de ReDoc (`/redoc`).
- [ ] Captura de `GET /users` → 200.
- [ ] Captura de `POST /users` con correo duplicado → 400.
- [ ] Captura de `POST /users` con datos inválidos → 422.
- [ ] Captura de `PUT /users/{id}` a usuario inexistente → 404.
- [ ] Captura de `PATCH /users/{id}` vacío → 400.
- [ ] Captura de `DELETE /users/{id}` a usuario inexistente → 404.

## Reflexión final sobre la evolución del proyecto

> Espacio para tu reflexión personal. Algunas preguntas que puedes responder:
> - ¿Qué cambió entre la versión anterior (solo GET/POST) y esta?
> - ¿Qué ventaja concreta trajo separar el código en `routes/schemas/services/dependencies/data` en vez de tenerlo todo junto?
> - ¿Cómo te ayudó `Depends()` a evitar código repetido?
> - ¿Qué tan útil fue Swagger UI para probar la API sin necesidad de Postman?
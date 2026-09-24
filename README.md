

# evidencias:

![alt text](<images5/Captura de pantalla 2026-09-23 002152.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 002208.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 161911.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 161931.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 162001.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 162622.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 162716.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 163110.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 163218.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 163356.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 165358.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 165710.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 170131.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 171751.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 172040.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 172523.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 172959.png>)
![alt text](<images5/Captura de pantalla 2026-09-23 173407.png>)

# device_systems

Este es mi proyecto **device_systems**: una API REST construida con FastAPI. La empecé con operaciones básicas sobre usuarios, la evolucioné con el CRUD completo, luego migré a persistencia real con SQLAlchemy, después agregué Alembic junto con los recursos de dispositivos y préstamos con relaciones y joins, y en esta última versión la transformé en una **API protegida**: autenticación con OAuth2 y JWT, contraseñas con hash, autorización por roles, CORS, middleware personalizado y rate limiting.

## Tecnologías utilizadas

- Python 3.11+
- FastAPI
- Uvicorn (servidor ASGI)
- Pydantic v2 (validación de datos)
- SQLAlchemy (ORM)
- Alembic (migraciones de base de datos)
- Passlib con bcrypt (hash de contraseñas)
- python-jose (JWT)
- slowapi (rate limiting)
- python-dotenv (variables de entorno)
- SQLite (motor de base de datos)
- Git y GitHub (control de versiones)

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── main.py                       # CORS, middleware, rate limiter y routers
│   ├── auth/
│   │   ├── auth_routes.py            # POST /auth/register, /login, GET /auth/me
│   │   ├── auth_service.py           # Lógica de registro y autenticación
│   │   └── security.py               # Hash de contraseñas y JWT
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   ├── user_model.py             # Ahora incluye hashed_password
│   │   ├── device_model.py
│   │   └── loan_model.py
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   ├── loan_schema.py
│   │   └── auth_schema.py            # UserRegister, UserLogin, Token, TokenData
│   ├── routes/
│   │   ├── user_routes.py            # Rutas protegidas con autenticación
│   │   ├── device_routes.py          # Rutas protegidas por rol
│   │   └── loan_routes.py            # Rutas protegidas por autenticación/rol
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py
│   ├── dependencies/
│   │   ├── database_dependency.py
│   │   └── auth_dependency.py        # get_current_user, get_current_active_user, require_roles
│   └── middlewares/
│       ├── request_middleware.py     # Cabeceras, tiempos de respuesta, request ID
│       └── rate_limiter.py           # Instancia compartida de slowapi
├── alembic/
│   └── versions/
├── alembic.ini
├── .env                               # Variables de entorno reales (NO se sube a Git)
├── .env.example                       # Plantilla de variables de entorno (sí se sube)
├── device_systems.db
├── requirements.txt
├── .gitignore
└── README.md
```

## Instalación

```bash
git clone <URL-de-mi-repositorio>
cd device_systems

python -m venv venv
source venv/Scripts/activate      # En Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
```

Antes de correr el proyecto, copio `.env.example` como `.env` y genero mi propia clave secreta:

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Pego el resultado en `.env`, en la variable `SECRET_KEY`.

## Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Migración de Alembic para los campos de autenticación

Como agregué `hashed_password` al modelo `User`, tuve que generar una nueva migración:

```bash
alembic revision --autogenerate -m "add authentication fields to users"
alembic upgrade head
```

En mi caso, como ya tenía datos de prueba de actividades anteriores sin ese campo, terminé recreando el historial de migraciones desde cero para evitar inconsistencias entre mi base de datos y lo que Alembic esperaba. Borré mi `device_systems.db` y las migraciones viejas, y generé una sola migración inicial que crea las tres tablas (`users`, `devices`, `loans`) ya con `hashed_password` incluido desde el principio.

## Hash de contraseñas y JWT (`app/auth/security.py`)

Nunca guardo ni muestro contraseñas en texto plano. Uso `passlib` con el esquema `bcrypt` para generar el hash:

```python
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

Para los tokens, uso `python-jose`:

```python
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

El `SECRET_KEY`, el algoritmo (`HS256`) y el tiempo de expiración los leo desde mi archivo `.env`, nunca los dejo escritos directamente en el código.

## Cómo funciona el login con OAuth2 y JWT

Implementé `POST /auth/login` usando `OAuth2PasswordRequestForm` de FastAPI en vez de un JSON simple. Esto es lo que hace que el botón **"Authorize"** de Swagger funcione automáticamente con el esquema OAuth2 estándar: en el formulario, el campo `username` recibe el correo electrónico, y `password` la contraseña. La respuesta es:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Ese token se envía luego en cada petición protegida, en la cabecera:
```
Authorization: Bearer <token>
```

`GET /auth/me` usa ese token para identificar quién soy, y devuelve mis datos sin el `hashed_password`.

## Protección de rutas y roles

Creé tres dependencias reutilizables en `app/dependencies/auth_dependency.py`:

- `get_current_user` — decodifica el token y busca al usuario. Si el token es inválido o no existe, responde `401`.
- `get_current_active_user` — además exige que el usuario esté activo.
- `require_roles(*roles)` — una "fábrica" de dependencias: genera una dependencia que exige que el usuario tenga uno de los roles indicados. Si no, responde `403`. A partir de ella definí `require_admin` y `require_admin_or_support`.

Así quedó la protección aplicada:

| Ruta | Protección |
|---|---|
| `GET /users` | Usuario autenticado |
| `GET /users/{user_id}` | Usuario autenticado |
| `POST /devices` | Admin o support |
| `PUT /devices/{device_id}` | Admin o support |
| `DELETE /devices/{device_id}` | Admin |
| `POST /loans` | Usuario autenticado |
| `PATCH /loans/{loan_id}/return` | Admin o support |
| `GET /loans/details` | Admin o support |

## CORS

Configuré `CORSMiddleware` en `main.py` para permitir, por ahora, solo mis orígenes de desarrollo local:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Por qué no usar `"*"` en producción cuando hay credenciales:** el estándar CORS prohíbe combinar un origen comodín (`allow_origins=["*"]`) con `allow_credentials=True`. Si se permitiera, cualquier sitio web en internet podría hacer peticiones a mi API llevando las credenciales del usuario (cookies o cabeceras de autorización) sin que el usuario lo supiera, ya que el navegador no bloquearía la petición por origen. Por eso, en producción, debo listar explícitamente cada dominio de confianza (por ejemplo, el dominio real de mi frontend), nunca un comodín, cuando la API maneja autenticación.

## Middleware personalizado (`app/middlewares/request_middleware.py`)

Implementé un middleware que se ejecuta en cada petición y agrega:

- `X-App-Name: device_systems`
- `X-Process-Time`: cuánto tardó la petición, en segundos
- `X-Request-ID`: un identificador único por petición (lo genero si el cliente no envió uno, o lo propago si ya venía)

También registro en la consola del servidor el método, la ruta y el código de estado de cada petición, lo cual me sirvió bastante para depurar errores durante el desarrollo.

## Rate limiting

Configuré `slowapi` con una instancia compartida de `Limiter` (`app/middlewares/rate_limiter.py`), y apliqué límites con el decorador `@limiter.limit(...)` en los endpoints más sensibles a abuso:

| Endpoint | Límite |
|---|---|
| `POST /auth/login` | 5 por minuto |
| `POST /auth/register` | 3 por minuto |
| `GET /users` | 30 por minuto |
| `POST /loans` | 10 por minuto |

Cuando se supera el límite, la API responde `429 Too Many Requests` con un mensaje indicando cuál era el límite excedido. Lo comprobé registrando 4 usuarios seguidos en menos de un minuto: los primeros 3 dieron `201`, y el cuarto dio `429` con el mensaje `"Rate limit exceeded: 3 per 1 minute"`.

## Validaciones de contraseña con Pydantic v2

En `app/schemas/auth_schema.py`, usé `field_validator` para exigir contraseñas seguras al registrarse:

```python
@field_validator("password")
@classmethod
def password_must_be_strong(cls, value: str) -> str:
    return _validate_password_strength(value)
```

La función valida: mínimo 8 caracteres, al menos una mayúscula, una minúscula, un número, y que no tenga espacios en blanco. También usé `model_config = ConfigDict(from_attributes=True)` (la sintaxis de Pydantic v2) en los schemas de respuesta, en vez de la vieja `class Config`.

## Códigos de estado usados

| Código | Significado en mi API |
|---|---|
| 200 OK | Operación exitosa |
| 201 Created | Registro creado exitosamente |
| 400 Bad Request | Dato duplicado o PATCH sin campos |
| 401 Unauthorized | Token ausente, inválido o credenciales incorrectas |
| 403 Forbidden | Usuario autenticado pero sin el rol necesario |
| 404 Not Found | El recurso solicitado no existe |
| 409 Conflict | Regla de negocio incumplida |
| 422 Unprocessable Entity | Datos de entrada inválidos |
| 429 Too Many Requests | Se superó el límite de peticiones |

## Manejo de errores implementado

- **Registro con email duplicado** → 400
- **Registro con contraseña débil** → 422, validado antes de tocar la base de datos
- **Login con credenciales incorrectas** → 401
- **Token ausente o inválido** → 401
- **Usuario autenticado sin el rol requerido** → 403
- **Superar el límite de peticiones** → 429

## Un problema real que resolví: incompatibilidad entre passlib y bcrypt

Durante las pruebas me encontré con un error `500` al registrar usuarios. El traceback mostraba `AttributeError: module 'bcrypt' has no attribute '__about__'`, seguido de `ValueError: password cannot be longer than 72 bytes`. Investigando, descubrí que era un problema de compatibilidad de versiones: `pip` había instalado la versión más reciente de `bcrypt` (5.0.0), que cambió su estructura interna y ya no es compatible con la versión de `passlib` que estaba usando. La solución fue fijar una versión anterior de `bcrypt`:

```bash
python -m pip install "bcrypt==4.0.1"
```

Este tipo de problema es común cuando se instalan dependencias sin fijar versiones exactas, y me hizo entender la importancia de revisar bien el `requirements.txt` en proyectos que dependen de librerías de seguridad.

## Flujo de ramas Git que usé en este proyecto

- **`main`**: rama estable con todo el historial de actividades anteriores ya fusionado.
- **`device_systems_security`**: rama donde desarrollé toda esta actividad (autenticación, JWT, roles, CORS, middleware, rate limiting), creada a partir de `main`. La fusioné directamente hacia `main` al terminar, tal como pidió esta guía.

## Reflexión final sobre la importancia de la seguridad en APIs REST

Antes de esta actividad, mi API funcionaba, pero cualquiera con la URL podía crear, modificar o borrar cualquier dato sin restricción alguna. Esta actividad me hizo ver la diferencia entre una API que "funciona" y una API que es segura para usarse en el mundo real.

Aprendí que nunca se debe guardar una contraseña tal cual la escribe el usuario: el hash con `bcrypt` significa que ni yo mismo, con acceso a la base de datos, puedo ver la contraseña original de alguien. También entendí por qué JWT es útil para APIs sin estado: el servidor no necesita recordar quién inició sesión, porque el propio token (firmado con mi `SECRET_KEY`) lleva la información necesaria y puede verificarse en cada petición sin consultar una sesión guardada en el servidor.

La autorización por roles me mostró que "estar autenticado" y "tener permiso para hacer algo" son dos preguntas distintas: un usuario puede tener un token válido (401 resuelto) y aun así no tener permiso para una acción específica (403). Separar esas dos dependencias (`get_current_active_user` vs `require_roles`) hizo que agregar nuevas reglas de permisos fuera tan simple como agregar un `Depends()` más a una ruta.

Finalmente, el rate limiting y el middleware personalizado me mostraron una capa de seguridad distinta: no se trata solo de quién puede hacer qué, sino de proteger la API contra el abuso (alguien intentando adivinar contraseñas a la fuerza, por ejemplo) y de tener trazabilidad de lo que pasa en cada petición mediante el `X-Request-ID` y los registros en consola.
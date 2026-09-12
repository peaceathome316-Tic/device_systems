

# evidencias:

![alt text](<images3/Captura de pantalla 2026-09-11 235624.png>)
![alt text](<images3/Captura de pantalla 2026-09-11 235718.png>)
![alt text](<images3/Captura de pantalla 2026-09-12 000157.png>)
![alt text](<images3/Captura de pantalla 2026-09-12 000336.png>)
![alt text](<images3/Captura de pantalla 2026-09-12 000522.png>)
![alt text](<images3/Captura de pantalla 2026-09-12 000634.png>)
![alt text](<images3/Captura de pantalla 2026-09-12 000850.png>)
![alt text](<images3/Captura de pantalla 2026-09-12 000953.png>)
![alt text](<images3/Captura de pantalla 2026-09-12 001041.png>)
![alt text](<images3/Captura de pantalla 2026-09-12 001147.png>)

# device_systems

Este es mi proyecto **device_systems**: una API REST para la gestión de usuarios, construida con FastAPI. La empecé con operaciones básicas (GET y POST), la evolucioné agregando el CRUD completo (PUT, PATCH, DELETE), manejo de errores y Dependency Injection, y en esta última versión la migré de datos en memoria a persistencia real con **SQLAlchemy** y una base de datos **SQLite**.

## Tecnologías utilizadas

- Python 3.11+
- FastAPI
- Uvicorn (servidor ASGI)
- Pydantic v2 (validación de datos)
- SQLAlchemy (ORM para la base de datos)
- SQLite (motor de base de datos)
- Git y GitHub (control de versiones)

## Estructura del proyecto

```
device_systems/
├── app/
│   ├── main.py                       # Punto de entrada: crea tablas, registra rutas y middleware
│   ├── database/
│   │   └── connection.py             # Engine, SessionLocal y Base de SQLAlchemy
│   ├── models/
│   │   └── user_model.py             # Modelo SQLAlchemy: representa la tabla 'users'
│   ├── schemas/
│   │   └── user_schema.py            # Schemas Pydantic de entrada y salida
│   ├── routes/
│   │   └── user_routes.py            # Endpoints de /users
│   ├── services/
│   │   └── user_service.py           # Lógica de negocio y consultas SQLAlchemy
│   └── dependencies/
│       └── database_dependency.py    # Dependencia get_db() con Depends()
├── device_systems.db                 # Base de datos SQLite (generada automáticamente, no versionada)
├── requirements.txt
├── .gitignore
└── README.md
```

Organicé el código en capas, cada una con una única responsabilidad:
- **routes**: recibe la petición HTTP y delega en `services`. No contiene lógica de negocio.
- **schemas**: valida lo que entra y define la forma de lo que sale por la API.
- **services**: contiene las reglas del negocio (correos duplicados, existencia del usuario) y las consultas a la base de datos.
- **dependencies**: lógica reutilizable inyectada con `Depends()`, como la sesión de base de datos.
- **database**: configuración de la conexión (engine, sesión, base declarativa).
- **models**: representación de las tablas reales en la base de datos.

## Instalación

```bash
git clone <URL-de-mi-repositorio>
cd device_systems

python -m venv venv
source venv/Scripts/activate      # En Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
```

## Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`. Al arrancar por primera vez, se crea automáticamente el archivo `device_systems.db` con la tabla `users`.

- Documentación interactiva (Swagger UI): `http://127.0.0.1:8000/docs`
- Documentación alternativa (ReDoc): `http://127.0.0.1:8000/redoc`

## Tabla de endpoints

| Operación | Método | Ruta | Código éxito | Código error |
|---|---|---|---|---|
| Listar usuarios (filtros `role`, `is_active`, orden `order_by`) | GET | `/users` | 200 OK | — |
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
  "username": "laura",
  "email": "laura@device.com",
  "role": "support",
  "is_active": true
}
```

Respuesta `201 Created`:
```json
{
  "username": "laura",
  "email": "laura@device.com",
  "role": "support",
  "is_active": true,
  "id": 1,
  "created_at": "2026-09-12T04:55:05.054374"
}
```

### Actualización parcial — `PATCH /users/{user_id}`

Request:
```json
{
  "is_active": false
}
```

Respuesta `200 OK`: el usuario completo con solo el campo `is_active` modificado; el resto de campos quedan igual.

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

| Código | Significado en mi API |
|---|---|
| 200 OK | Operación exitosa (GET, PUT, PATCH, DELETE) |
| 201 Created | Usuario creado exitosamente |
| 400 Bad Request | Correo duplicado o PATCH sin campos |
| 404 Not Found | El usuario solicitado no existe |
| 422 Unprocessable Entity | Datos de entrada inválidos (validación de Pydantic) |

## Uso de Dependency Injection (`Depends()`)

Creé la función `get_db` en `app/dependencies/database_dependency.py` para entregar una sesión de base de datos a cada endpoint y cerrarla automáticamente al terminar:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

La inyecto con `Depends(get_db)` en todos los endpoints de `user_routes.py`. Esto me evita abrir y cerrar sesiones manualmente en cada ruta, y garantiza que la sesión se cierre incluso si ocurre un error durante la petición.

## Diferencia entre modelo SQLAlchemy y schema Pydantic

Aunque ambos describen la forma de un "usuario", en mi proyecto cumplen roles distintos:

- **Modelo SQLAlchemy** (`app/models/user_model.py`): representa una **tabla real en la base de datos**. Defino ahí las columnas, sus tipos (`Integer`, `String`, `Boolean`, `DateTime`) y restricciones a nivel de base de datos (`nullable=False`, `unique=True`). Es lo que SQLAlchemy usa para generar el SQL y guardar o leer filas en `device_systems.db`.

- **Schema Pydantic** (`app/schemas/user_schema.py`): representa la **forma de los datos que entran y salen por la API** (el JSON del request/response). No tiene relación directa con la base de datos; su trabajo es validar lo que envía el cliente (`UserCreate`, `UserPatch`) y darle forma a lo que devuelvo (`UserResponse`).

En resumen: el modelo le habla a la base de datos, y el schema le habla al cliente de la API. Por eso pude definir `role` como `String` en el modelo (columna de texto simple) y como un `Enum` (`UserRole`) en el schema (para validar que solo se acepten `admin`, `support` o `user`). Separarlos me permite cambiar cómo valido la entrada sin tener que tocar la estructura de la tabla, y viceversa.

## Manejo de errores implementado

Controlo todos los errores previsibles con `HTTPException`, devolviendo siempre un JSON consistente `{"detail": "..."}`:

- **Usuario no encontrado** → 404, validado en `user_service.get_user_by_id` antes de cualquier operación sobre ese usuario.
- **Correo electrónico duplicado** → 400, verificado en `user_service.py` tanto en creación (`POST`) como en reemplazo (`PUT`) y actualización parcial (`PATCH`), consultando directamente contra la base de datos.
- **Actualización sin datos (PATCH vacío)** → 400, validado en `update_user_partial`.
- **Datos inválidos** (email mal formado, campos faltantes, rol no permitido) → 422, generado automáticamente por la validación de Pydantic antes de que la petición llegue a mi código.

Además, un middleware en `main.py` agrega las cabeceras `X-App-Name` y `X-API-Version` a todas las respuestas, incluidas las de error.

## Flujo de ramas Git que usé en este proyecto

- **`main`**: contiene únicamente la versión inicial del proyecto. No la toco directamente.
- **`develop`**: rama de integración, donde se fusiona cada actividad ya probada.
- **Ramas `feature`**: cada evolución del proyecto la desarrollé en su propia rama (`feature` para el CRUD completo, `db9_feature` para la migración a base de datos), y la fusioné a `develop` una vez probada.


## Reflexión final sobre la importancia de la persistencia en una API

Trabajar con datos en memoria me ha sirvió para aprender la lógica de los endpoints, pero tenía una limitación grande, toda la información se perdía cada vez que reiniciaba el servidor. Migrar a SQLAlchemy con SQLite me hizo entender que una API real necesita persistencia — los datos deben sobrevivir más allá de la ejecución del programa.

También aprendí que separar el modelo (base de datos) del schema (API) no es una complicación innecesaria, sino lo que me permite que ambas partes evolucionen de forma independiente. Usar un ORM como SQLAlchemy en vez de escribir SQL a mano me pareció más seguro (evita inyecciones SQL) y más fácil de mantener, porque las consultas quedan escritas como código Python en vez de strings de SQL sueltos por el proyecto.

Por otro lado, `Depends()` creo que volvió a demostrarme su utilidad: antes lo usé para evitar repetir la búsqueda de usuarios, y ahora lo usé para manejar la sesión de base de datos sin tener que abrirla y cerrarla manualmente en cada endpoint. Y trabajar con ramas Git (`main`, `develop`, `feature`) me ayudó otra vez a probar todos estos cambios grandes sin arriesgar la versión estable del proyecto.
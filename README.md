

# evidencias:

![alt text](<images4/Captura de pantalla 2026-09-18 010750.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 010828.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 183039.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 183138.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 183254.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 183346.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 183637.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 183903.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 184008.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 184118.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 184516.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 184835.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 185031.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 185811.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 190206.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 190345.png>)
![alt text](<images4/Captura de pantalla 2026-09-18 190622.png>)

# device_systems

Este es mi proyecto **device_systems**: una API REST construida con FastAPI. La empecé con operaciones básicas sobre usuarios (GET y POST), la evolucioné con el CRUD completo (PUT, PATCH, DELETE) y Dependency Injection, luego migré la persistencia de memoria a una base de datos real con SQLAlchemy, y en esta última versión agregué **migraciones controladas con Alembic**, dos recursos nuevos (**dispositivos** y **préstamos**), relaciones entre modelos y **consultas con joins**.

## Tecnologías utilizadas

- Python 3.11+
- FastAPI
- Uvicorn (servidor ASGI)
- Pydantic v2 (validación de datos)
- SQLAlchemy (ORM)
- Alembic (migraciones de base de datos)
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
│   │   ├── user_model.py             # Modelo User (con relación a Loan)
│   │   ├── device_model.py           # Modelo Device (con relación a Loan)
│   │   └── loan_model.py             # Modelo Loan (con ForeignKey a User y Device)
│   ├── schemas/
│   │   ├── user_schema.py
│   │   ├── device_schema.py
│   │   └── loan_schema.py            # Incluye LoanDetailResponse (para las consultas con joins)
│   ├── routes/
│   │   ├── user_routes.py            # Incluye GET /users/{id}/loans
│   │   ├── device_routes.py          # Incluye GET /devices/{id}/loans
│   │   └── loan_routes.py
│   ├── services/
│   │   ├── user_service.py
│   │   ├── device_service.py
│   │   └── loan_service.py           # Reglas de negocio de préstamos y consultas con joins
│   └── dependencies/
│       └── database_dependency.py
├── alembic/
│   ├── versions/                     # Migraciones generadas automáticamente
│   └── env.py                        # Configurado para reconocer mis modelos SQLAlchemy
├── alembic.ini
├── device_systems.db                 # Base de datos SQLite (no versionada)
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

## Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

- Documentación interactiva (Swagger UI): `http://127.0.0.1:8000/docs`
- Documentación alternativa (ReDoc): `http://127.0.0.1:8000/redoc`

## Migraciones con Alembic

Configuré Alembic para que reconozca la URL de mi base de datos y la metadata de mis modelos SQLAlchemy. En `alembic.ini` apunté la conexión a mi base de datos SQLite:

```ini
sqlalchemy.url = sqlite:///./device_systems.db
```

Y en `alembic/env.py` importé mi `Base` y mis modelos, y reemplacé `target_metadata = None` por:

```python
from app.database.connection import Base
from app.models import user_model, device_model, loan_model

target_metadata = Base.metadata
```

Esto le permite a Alembic comparar mis modelos contra el estado real de la base de datos y generar automáticamente el SQL necesario para igualarlos.

### Comandos que usé

Inicializar Alembic:
```bash
alembic init alembic
```

Como ya tenía la tabla `users` creada manualmente antes de instalar Alembic, marqué ese estado como punto de partida sin generar cambios reales:
```bash
alembic stamp head
```

Generar la migración para las tablas nuevas:
```bash
alembic revision --autogenerate -m "create devices and loans tables"
```

Aplicar la migración:
```bash
alembic upgrade head
```

Consultar el historial de migraciones:
```bash
alembic history
```

## Modelo de datos y asociaciones

Además del modelo `User` que ya tenía, agregué dos modelos nuevos:

**`Device`** — representa los dispositivos tecnológicos disponibles para préstamo:

| Campo | Tipo | Restricción |
|---|---|---|
| id | Integer | Primary Key |
| name | String | Obligatorio |
| serial_number | String | Único y obligatorio |
| device_type | String | Obligatorio |
| brand | String | Opcional |
| is_available | Boolean | Por defecto `True` |
| created_at | DateTime | Fecha de creación |

**`Loan`** — representa el préstamo de un dispositivo a un usuario:

| Campo | Tipo | Restricción |
|---|---|---|
| id | Integer | Primary Key |
| user_id | Integer | Foreign Key a `users.id` |
| device_id | Integer | Foreign Key a `devices.id` |
| loan_date | DateTime | Fecha de préstamo |
| return_date | DateTime | Opcional |
| status | String | `active`, `returned` u `overdue` |

### Relaciones que definí

Un usuario puede tener muchos préstamos, y un dispositivo puede aparecer en muchos préstamos históricos. Cada préstamo, a su vez, pertenece exactamente a un usuario y a un dispositivo. Implementé esto con `relationship()` y `back_populates` en los tres modelos:

```python
# En User
loans = relationship("Loan", back_populates="user")

# En Device
loans = relationship("Loan", back_populates="device")

# En Loan
user = relationship("User", back_populates="loans")
device = relationship("Device", back_populates="loans")
```

La `ForeignKey` en `Loan` (`user_id` y `device_id`) es lo que garantiza la integridad referencial a nivel de base de datos: un préstamo no puede apuntar a un usuario o dispositivo que no exista.

## Tabla de endpoints

### Users
| Operación | Método | Ruta |
|---|---|---|
| Listar / filtrar / ordenar | GET | `/users` |
| Consultar por ID | GET | `/users/{user_id}` |
| **Consultar préstamos de un usuario (join)** | GET | `/users/{user_id}/loans` |
| Crear | POST | `/users` |
| Actualizar completo | PUT | `/users/{user_id}` |
| Actualizar parcial | PATCH | `/users/{user_id}` |
| Eliminar | DELETE | `/users/{user_id}` |

### Devices
| Operación | Método | Ruta |
|---|---|---|
| Listar / filtrar (`device_type`, `is_available`, `brand`, `search`) | GET | `/devices` |
| Consultar por ID | GET | `/devices/{device_id}` |
| **Historial de préstamos del dispositivo (join)** | GET | `/devices/{device_id}/loans` |
| Crear | POST | `/devices` |
| Actualizar completo | PUT | `/devices/{device_id}` |
| Actualizar parcial | PATCH | `/devices/{device_id}` |
| Eliminar | DELETE | `/devices/{device_id}` |

### Loans
| Operación | Método | Ruta |
|---|---|---|
| Listar / filtrar (`status`, `user_id`, `device_id`) | GET | `/loans` |
| **Listar con información relacionada (join)** | GET | `/loans/details` |
| Consultar por ID | GET | `/loans/{loan_id}` |
| Crear préstamo | POST | `/loans` |
| Registrar devolución | PATCH | `/loans/{loan_id}/return` |

## Ejemplos de peticiones y respuestas

### Crear un préstamo — `POST /loans`

Request:
```json
{
  "user_id": 1,
  "device_id": 1
}
```

Respuesta `201 Created`:
```json
{
  "id": 1,
  "user_id": 1,
  "device_id": 1,
  "loan_date": "2026-09-18T23:00:00",
  "return_date": null,
  "status": "active"
}
```

Al crear el préstamo, el dispositivo asociado cambia automáticamente a `is_available: false`.

### Consulta con join — `GET /loans/details`

Respuesta `200 OK`:
```json
[
  {
    "loan_id": 1,
    "status": "active",
    "loan_date": "2026-09-18T23:00:00",
    "return_date": null,
    "user": {
      "id": 1,
      "username": "ana",
      "email": "ana@device.com"
    },
    "device": {
      "id": 1,
      "name": "Laptop Lenovo ThinkPad",
      "serial_number": "LEN-2024-001",
      "device_type": "laptop"
    }
  }
]
```

Esta respuesta combina información de las tres tablas (`loans`, `users`, `devices`) en una sola consulta, usando `.join()` de SQLAlchemy.

### Intentar prestar un dispositivo no disponible — error controlado

Respuesta `409 Conflict`:
```json
{
  "detail": "El dispositivo con ID 1 no está disponible para préstamo."
}
```

### Intentar devolver un préstamo ya devuelto — error controlado

Respuesta `409 Conflict`:
```json
{
  "detail": "El préstamo con ID 1 ya fue devuelto anteriormente."
}
```

## Códigos de estado usados

| Código | Significado en mi API |
|---|---|
| 200 OK | Operación exitosa |
| 201 Created | Registro creado exitosamente |
| 400 Bad Request | Dato duplicado (correo, número de serie) o PATCH sin campos |
| 404 Not Found | El recurso solicitado no existe |
| 409 Conflict | Regla de negocio incumplida (dispositivo no disponible, préstamo ya devuelto) |
| 422 Unprocessable Entity | Datos de entrada inválidos (validación de Pydantic) |

Agregar el 409 fue algo nuevo para mí: lo usé específicamente para diferenciar "el dato ya existe" (400) de "la operación no se puede hacer en este momento por una regla de negocio" (409), que son situaciones distintas.

## Consultas con joins y filtros que implementé

En `loan_service.py` combiné información de varias tablas usando `.join()`, cargando las relaciones con `joinedload()` para traer usuario y dispositivo en la misma consulta:

```python
query = (
    db.query(Loan)
    .join(User, Loan.user_id == User.id)
    .join(Device, Loan.device_id == Device.id)
    .options(joinedload(Loan.user), joinedload(Loan.device))
)
```

Sobre esa base, apliqué filtros opcionales según los parámetros que llegan por query string:

```python
if status_filter is not None:
    query = query.filter(Loan.status == status_filter)
if user_email is not None:
    query = query.filter(User.email.ilike(f"%{user_email}%"))
if device_type is not None:
    query = query.filter(Device.device_type == device_type)
```

Usé `ilike()` para las búsquedas de texto (como el correo o el nombre del dispositivo), porque permite coincidencias parciales sin importar mayúsculas o minúsculas.

## Manejo de errores implementado

Controlo todos los errores con `HTTPException`, devolviendo siempre `{"detail": "..."}`:

- **Usuario o dispositivo inexistente** → 404
- **Dispositivo no disponible para préstamo** → 409
- **Préstamo inexistente** → 404
- **Intento de devolver un préstamo ya devuelto** → 409
- **Número de serie duplicado** → 400
- **Datos inválidos** (tipo de dispositivo no permitido, email mal formado) → 422, automático por Pydantic

## Flujo de ramas Git que usé en este proyecto

- **`main`**: contenía solo la versión inicial del proyecto hasta esta actividad.
- **`develop`**: rama de integración de las actividades anteriores (CRUD completo y persistencia con SQLAlchemy).
- **`device_systems_alembic_relaciones`**: rama donde desarrollé esta actividad completa (Alembic, modelos relacionados, joins). A diferencia de las actividades anteriores, esta rama la fusioné directamente hacia `main`, tal como lo pidió esta guía.

## Reflexión sobre la importancia de migraciones, relaciones y consultas avanzadas

Antes de esta actividad, cada vez que cambiaba un modelo tenía que borrar la base de datos y dejar que SQLAlchemy la recreara desde cero — algo que en un proyecto real, con datos ya guardados, sería inaceptable. Alembic me mostró cómo versionar esos cambios: cada migración queda registrada, se puede aplicar, revisar en el historial, y en teoría revertir si algo sale mal. Es la diferencia entre "reconstruir la base de datos" y "evolucionarla".

Las relaciones entre modelos (`relationship()`, `back_populates`, `ForeignKey`) me permitieron modelar algo que en la vida real tiene sentido: un préstamo no existe por sí solo, siempre pertenece a un usuario y a un dispositivo. Antes de esto, hubiera tenido que manejar esa conexión a mano, cruzando IDs manualmente en el código. Con las relaciones, SQLAlchemy me permite navegar de un préstamo a su usuario y su dispositivo (o al revés) de forma directa.

Finalmente, las consultas con joins me mostraron por qué separar los datos en varias tablas no significa que la API tenga que devolver información fragmentada. Pude combinar usuario, dispositivo y préstamo en una sola respuesta (`LoanDetailResponse`), que es justamente lo que un cliente de la API necesitaría ver de un vistazo, sin tener que hacer tres peticiones separadas y unir la información él mismo.
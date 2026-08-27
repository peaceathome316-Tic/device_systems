device_systems

API REST desarrollada con FastAPI para la gestión del recurso usuarios del sistema device_systems. Implementa validación de datos con Pydantic v2, path parameters, query parameters, response_model y cabeceras HTTP personalizadas.

Descripción de la aplicación

device_systems expone endpoints GET y POST sobre el recurso users, permitiendo:

Listar todos los usuarios registrados.
Consultar un usuario específico mediante su ID (path parameter).
Filtrar usuarios por rol y por estado activo/inactivo (query parameters).
Registrar un nuevo usuario, validando los datos con Pydantic y evitando correos duplicados.
Retornar respuestas estandarizadas mediante response_model, ocultando datos sensibles como la contraseña.
Incluir cabeceras HTTP personalizadas en todas las respuestas del recurso.

evidencias:
![alt text](<images/Captura de pantalla 2026-08-22 082610.png>)
![alt text](<images/Captura de pantalla 2026-08-26 194509.png>)
![alt text](<images/Captura de pantalla 2026-08-26 194621.png>)

La persistencia se simula en memoria con una lista de diccionarios (db_users); no hay base de datos real.

Estructura del proyecto
device_systems/
│── app/
│   │── main.py
│   │── schemas/
│   │   │── user_schema.py
│   │── routes/
│   │   │── user_routes.py
│── pyproject.toml
│── uv.lock
│── README.md
Instalación de dependencias

Requisitos: Python >= 3.13 y uv instalado.

Dependencias (pyproject.toml):

fastapi >= 0.141.1
pydantic[email] >= 2.13.4
uvicorn[standard] >= 0.52.4
bash
git clone <https://github.com/peaceathome316-Tic/device_systems.git>
cd device_systems
uv sync
Ejecución del servidor
bash
uv run uvicorn app.main:app --reload
API: http://127.0.0.1:8000
Swagger UI: http://127.0.0.1:8000/docs
Redoc: http://127.0.0.1:8000/redoc
Modelo de usuario (Pydantic)
Campo	Tipo	Reglas
username	str	Obligatorio, entre 3 y 50 caracteres
email	EmailStr	Obligatorio, formato de correo válido
role	UserRole (enum)	admin, operator, user — default operator
is_active	bool	Default true
password	str	Solo en UserCreate, mínimo 6 caracteres
id	int	Solo en UserResponse, asignado por el servidor

Esquemas usados: UserCreate (entrada del POST, incluye password), UserUpdate (campos opcionales, definido pero sin endpoint aún) y UserResponse (salida, sin password).

Tabla de endpoints
Método	Ruta	Descripción	Parámetros	Respuestas
GET	/	Health check de la API	—	200 OK
GET	/users/	Lista usuarios, con filtros opcionales	Query: role (admin|operator|user), is_active (true|false)	200 OK
GET	/users/{user_id}	Consulta un usuario por ID	Path: user_id (int)	200 OK / 404 Not Found
POST	/users/	Registra un nuevo usuario	Body: UserCreate	201 Created / 400 Bad Request (email duplicado) / 422 Unprocessable Entity (validación)
Cabeceras personalizadas

Todos los endpoints de /users retornan:

X-App-Name: device_systems
X-API-Version: 1.0

Se inyectan en cada endpoint mediante el parámetro Response de FastAPI, en la función set_custom_headers().

Ejemplos de peticiones

GET /users/

bash
curl http://127.0.0.1:8000/users/

GET /users/ con filtros

bash
curl "http://127.0.0.1:8000/users/?role=admin"
curl "http://127.0.0.1:8000/users/?is_active=true"

GET /users/{user_id}

bash
curl http://127.0.0.1:8000/users/1

404 si no existe:

json
{ "detail": "Usuario con ID 99 no encontrado." }

POST /users/

bash
curl -X POST http://127.0.0.1:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{
        "username": "johndoe",
        "email": "john@example.com",
        "role": "operator",
        "is_active": true,
        "password": "secret123"
      }'

201 Created:

json
{
  "username": "johndoe",
  "email": "john@example.com",
  "role": "operator",
  "is_active": true,
  "id": 2
}

400 si el email ya existe:

json
{ "detail": "El correo electrónico ya está registrado en device_systems." }
Nota técnica

El usuario precargado en db_users usa la clave "name", pero UserBase espera "username". Esto rompe la validación de response_model=UserResponse en los endpoints GET hasta corregir la clave en el diccionario inicial.
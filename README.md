# FastAPI Template / Boilerplate

Plantilla base (*boilerplate*) para el desarrollo ágil de APIs REST modernas y escalables con **FastAPI**, **SQLAlchemy 2.0** y **PostgreSQL**. Diseñada con una arquitectura limpia por capas (rutas, controladores, modelos y esquemas).

---

## 🚀 Características

- **FastAPI**: Alto rendimiento, tipado estricto y documentación interactiva automática.
- **SQLAlchemy 2.0**: ORM moderno utilizando `Mapped` y `mapped_column`.
- **PostgreSQL + Psycopg 3**: Conexión eficiente a base de datos relacional con el driver moderno `psycopg`.
- **Pydantic v2**: Validación y serialización rápida de datos.
- **Pydantic Settings**: Gestión centralizada y fuertemente tipada de variables de entorno mediante `.env`.
- **Arquitectura Modular**: Separación clara de responsabilidades:
  - `api/`: Definición de rutas y endpoints.
  - `controllers/`: Lógica de negocio y consultas a la base de datos.
  - `models/`: Modelos de tablas SQLAlchemy.
  - `schemas/`: DTOs y validaciones Pydantic.
  - `core/`: Configuración y sesión de base de datos.

---

## 📁 Estructura del Proyecto

```text
fast_api_template/
├── app/
│   ├── api/                     # Rutas / Endpoints de la API
│   │   ├── test_routes.py
│   │   └── user_routes.py
│   ├── controllers/             # Lógica de negocio
│   │   ├── test_controller.py
│   │   └── user_controller.py
│   ├── core/                    # Configuraciones centrales
│   │   ├── config.py            # Variables de entorno con Pydantic Settings
│   │   └── database_connection.py # Configuración y sesión de SQLAlchemy
│   ├── models/                  # Modelos de base de datos (SQLAlchemy)
│   │   ├── test_model.py
│   │   └── user_model.py
│   ├── schemas/                 # Esquemas de entrada y salida (Pydantic)
│   │   ├── test_schema.py
│   │   └── user_schema.py
│   └── main.py                  # Punto de entrada de la aplicación FastAPI
├── .env.example                 # Plantilla de variables de entorno
├── requirements.txt             # Dependencias del proyecto
└── README.md
```

---

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.10** o superior
- **PostgreSQL** (en ejecución localmente o mediante Docker)

---

## ⚙️ Pasos para Ejecutar el Proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/fast_api_template.git
cd fast_api_template
```

### 2. Crear y activar un entorno virtual

- **En Windows (PowerShell):**
  ```powershell
  python -m venv env
  .\env\Scripts\Activate.ps1
  ```

- **En Linux / macOS:**
  ```bash
  python3 -m venv env
  source env/bin/activate
  ```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Copia el archivo `.env.example` y renómbralo a `.env`:

- **En Windows (PowerShell):**
  ```powershell
  Copy-Item .env.example .env
  ```

- **En Linux / macOS:**
  ```bash
  cp .env.example .env
  ```

Abre el archivo `.env` y ajusta las credenciales de conexión a tu base de datos PostgreSQL:

```env
APP_NAME=API_TEMPLATE
APP_VERSION=1.0.0
APP_DESCRIPTION=BOILERPLATE_FASTAPI_BASED

DB_HOST=localhost
DB_PORT=5432
DB_NAME=tu_base_de_datos
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DRIVER_NAME=postgresql+psycopg
```

> **Nota:** Asegúrate de que la base de datos especificada en `DB_NAME` exista en tu servidor PostgreSQL antes de iniciar la aplicación. Las tablas se crearán automáticamente al arrancar.

### 5. Iniciar el servidor de desarrollo

Ejecuta el servidor ASGI **Uvicorn** con recarga automática:

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible por defecto en: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📖 Documentación Interactiva

FastAPI genera documentación interactiva lista para probar en el navegador:

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📌 Endpoints Disponibles

### Estado del Sistema
- `GET /health/db` - Verifica la conexión con la base de datos PostgreSQL.

### Restaurantes (`/restaurants`)
- `POST /restaurants/` - Crear un nuevo restaurante.
- `GET /restaurants/` - Listar restaurantes con paginación (`skip`, `limit`).
- `GET /restaurants/{id_rest}` - Obtener un restaurante por su ID.
- `PUT /restaurants/{id_rest}` - Actualizar datos de un restaurante.
- `DELETE /restaurants/{id_rest}` - Eliminar un restaurante.

### Usuarios (`/users`)
- `POST /users/` - Crear un nuevo usuario (requiere un `id_rest_user` válido).
- `GET /users/` - Listar usuarios con paginación (`skip`, `limit`).
- `GET /users/{id_user}` - Obtener un usuario por su ID.
- `PUT /users/{id_user}` - Actualizar datos de un usuario.
- `DELETE /users/{id_user}` - Eliminar un usuario.

### Pruebas (`/test`)
- `POST /test/` - Crear un registro de prueba.

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia [MIT](LICENSE).


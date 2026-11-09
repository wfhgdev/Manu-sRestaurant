# Manu's Restaurant API

API REST para la gestión de restaurantes construida con **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, **Alembic** (migraciones) y **Faker** (datos de prueba). Arquitectura por capas: rutas, controladores, modelos y esquemas.

---

## 🚀 Características

- **FastAPI**: Alto rendimiento, tipado estricto y documentación interactiva automática.
- **SQLAlchemy 2.0**: ORM moderno utilizando `Mapped` y `mapped_column`.
- **PostgreSQL + Psycopg 3**: Conexión a base de datos relacional con el driver `psycopg`.
- **Pydantic v2 + Pydantic Settings**: Validación de datos y variables de entorno desde `.env`.
- **Alembic**: Las tablas se crean y modifican mediante migraciones versionadas.
- **Seeders**: llenan la base de datos con datos fijos de demostración (respetando las relaciones entre tablas) y con datos falsos de **Faker**.
- **Pytest**: Tests automáticos en `tests/`.

---

## 📁 Estructura del Proyecto

```text
Manu-sRestaurant/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada de la aplicación FastAPI
│   ├── dependencies.py            # Dependencias compartidas (Depends)
│   ├── routers/                   # Rutas / Endpoints de la API
│   │   ├── __init__.py
│   │   ├── restaurant_routes.py
│   │   ├── test_routes.py
│   │   └── user_routes.py
│   ├── internal/                  # Rutas internas de administración
│   │   ├── __init__.py
│   │   └── admin.py
│   ├── core/                      # Configuración central
│   │   ├── __init__.py
│   │   ├── config.py              # Variables de entorno con Pydantic Settings
│   │   ├── database_connection.py # Engine, sesión y Base de SQLAlchemy
│   │   └── security.py            # (pendiente) contraseñas y tokens
│   ├── models/                    # Modelos de base de datos (SQLAlchemy)
│   │   ├── __init__.py            # Importa TODOS los modelos (lo usa Alembic)
│   │   ├── booking_model.py
│   │   ├── category_model.py
│   │   ├── dish_model.py
│   │   ├── menu_model.py
│   │   ├── restaurant_model.py
│   │   ├── shift_model.py
│   │   ├── table_model.py
│   │   ├── test_model.py
│   │   └── user_model.py
│   ├── schemas/                   # Esquemas de entrada y salida (Pydantic)
│   │   ├── __init__.py
│   │   ├── enums.py
│   │   ├── restaurant_schema.py
│   │   ├── test_schema.py
│   │   └── user_schema.py
│   ├── controllers/               # Operaciones sobre la base de datos
│   │   ├── __init__.py
│   │   ├── restaurant_controller.py
│   │   ├── test_controller.py
│   │   └── user_controller.py
│   ├── services/                  # Lógica de negocio reutilizable
│   │   ├── __init__.py
│   │   └── item_service.py
│   └── db/
│       ├── __init__.py
│       ├── database.py            # Base + todos los modelos cargados
│       └── migrations/            # Migraciones de Alembic
│           ├── env.py
│           ├── script.py.mako
│           └── versions/
├── seeders/                       # Datos iniciales y de prueba
│   ├── __init__.py
│   ├── factories/
│   │   ├── __init__.py
│   │   └── test_factory.py        # Faker: inventa un registro de la tabla test
│   ├── allergen_seeder.py         # Los 14 alérgenos oficiales (datos fijos)
│   ├── demo_seeder.py             # Restaurante de demo completo (datos fijos)
│   ├── test_seeder.py             # Registros falsos para la tabla test
│   └── run.py                     # Lanzador: python -m seeders.run
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_test.py
├── .env.example                   # Plantilla de variables de entorno
├── .gitignore
├── alembic.ini                    # Configuración de Alembic
├── requirements.txt
├── README.md
└── run.sh                         # Levanta el servidor
```

---

## 🛠️ Requisitos Previos

- **Python 3.10** o superior
- **PostgreSQL** en ejecución (local o Docker)

---

## ⚙️ Pasos para Ejecutar el Proyecto

### 1. Clonar el repositorio

```bash
git clone https://github.com/wfhgdev/Manu-sRestaurant.git
cd Manu-sRestaurant
```

### 2. Crear y activar un entorno virtual

- **En Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```

- **En Linux / macOS / Git Bash:**
  ```bash
  python -m venv .venv
  source .venv/bin/activate      # en Git Bash (Windows): source .venv/Scripts/activate
  ```

Comprobar que se usa el Python del entorno virtual:

```bash
python -c "import sys; print(sys.executable)"
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Copia `.env.example` como `.env`:

- **En Windows (PowerShell):** `Copy-Item .env.example .env`
- **En Linux / macOS:** `cp .env.example .env`

Y ajusta las credenciales de tu PostgreSQL:

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

### 5. Crear la base de datos y las tablas (Alembic)

La base de datos indicada en `DB_NAME` debe existir. Si no existe, créala (pgAdmin o terminal):

```bash
psql -U postgres -h localhost -c "CREATE DATABASE tu_base_de_datos;"
```

Crea las tablas aplicando las migraciones:

```bash
alembic upgrade head
```

> **Nota:** si tu base de datos ya tenía las tablas creadas de antes (cuando se creaban solas al arrancar), en lugar de `upgrade head` ejecuta `alembic stamp head` para marcarla como actualizada.

### 6. (Opcional) Llenar con datos de prueba

**Restaurante de demostración (datos fijos):**

```bash
python -m seeders.run --demo
```

Inserta los 14 alérgenos oficiales y un restaurante completo ("Manu's Restaurant"): 3 usuarios, 4 categorías, 8 platos con sus alérgenos, un menú del día, 5 mesas, 2 turnos con camareros y mesas asignadas, y 3 reservas. Se puede ejecutar varias veces: si el restaurante ya existe, no inserta nada.

Usuarios de demo:

| Nombre | Email | Contraseña | Rol |
|---|---|---|---|
| Manuel García | manu@manusrestaurant.es | admin1234 | administrador |
| Ana López | ana@manusrestaurant.es | camarero1234 | camarero |
| Luis Pérez | luis@manusrestaurant.es | camarero1234 | camarero |

> Los objetos se enlazan entre sí (`restaurant=manus`, `allergens=[...]`) en lugar de escribir ids a mano, así SQLAlchemy rellena las claves foráneas y las tablas intermedias automáticamente.

**Registros falsos con Faker (tabla `test`):**

```bash
python -m seeders.run --count 100
```

### 7. Iniciar el servidor de desarrollo

```bash
uvicorn app.main:app --reload
# o bien:
bash run.sh
```

Disponible en: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 8. Ejecutar los tests

```bash
pytest
```

---

## 🔄 Migraciones con Alembic

| Comando                                    | Para qué                             |
| ------------------------------------------ | ------------------------------------ |
| `alembic revision --autogenerate -m "msg"` | Crear migración tras cambiar modelos |
| `alembic upgrade head`                     | Aplicar todas las pendientes         |
| `alembic downgrade -1`                     | Deshacer la última                   |
| `alembic current`                          | Ver versión actual                   |
| `alembic history`                          | Ver historial                        |

Ejecuta `alembic` siempre desde la raíz del proyecto.

**Orden de trabajo para una entidad nueva:** model → importarlo en `app/models/__init__.py` → `alembic revision --autogenerate` → revisar el archivo generado → `alembic upgrade head` → schema → controller → router → `include_router` en `main.py`.

---

## 📖 Documentación Interactiva

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📌 Endpoints Disponibles

### General
- `GET /` - Mensaje de bienvenida.
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

### Relación Turno-Mesa (`/shift-table-rels`)
- `POST /shift-table-rels/` - Crear una nueva relación turno-mesa (valida `id_assign_shift_table_rel` e `id_table_shift_table_rel`).
- `GET /shift-table-rels/` - Listar relaciones turno-mesa con paginación (`skip`, `limit`) y filtros opcionales (`id_assign`, `id_table`).
- `GET /shift-table-rels/{id_shift_table_rel}` - Obtener una relación por su ID.
- `PUT /shift-table-rels/{id_shift_table_rel}` - Actualizar datos de una relación.
- `DELETE /shift-table-rels/{id_shift_table_rel}` - Eliminar una relación.

### Pruebas (`/test`)
- `GET /test/` - Ruta de prueba.
- `POST /test/` - Crear un registro de prueba.

---

## 🧾 Cheatsheet

```bash
source .venv/bin/activate                 # activar venv (Windows: .\.venv\Scripts\Activate.ps1)
pip freeze > requirements.txt             # actualizar dependencias
uvicorn app.main:app --reload             # levantar API
alembic revision --autogenerate -m "msg"  # nueva migración
alembic upgrade head                      # aplicar migraciones
python -m seeders.run --demo              # restaurante de demo (datos fijos)
python -m seeders.run --count 100         # datos falsos con Faker (tabla test)
pytest                                    # ejecutar tests
```

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia [MIT](LICENSE).

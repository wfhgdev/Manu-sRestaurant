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
- **Manejo de errores**: los errores de base de datos (datos inválidos, claves duplicadas o relaciones rotas) devuelven una respuesta clara en lugar de un error 500.
- **Pytest**: Tests automáticos en `tests/`.

---

## 📁 Estructura del Proyecto

```text
Manu-sRestaurant/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada: crea la app y registra todas las rutas
│   ├── dependencies.py            # Dependencias compartidas (Depends)
│   ├── routers/                   # Rutas / Endpoints de la API (una por entidad)
│   │   ├── __init__.py
│   │   ├── allergen_routes.py
│   │   ├── booking_routes.py
│   │   ├── category_routes.py
│   │   ├── dish_routes.py
│   │   ├── menu_detail_routes.py
│   │   ├── menu_routes.py
│   │   ├── restaurant_routes.py
│   │   ├── shift_assignment_routes.py
│   │   ├── shift_table_rel_routes.py
│   │   ├── table_rel_routes.py
│   │   ├── table_routes.py
│   │   ├── test_routes.py
│   │   └── user_routes.py
│   ├── controllers/               # Operaciones sobre la base de datos (una por entidad)
│   │   ├── __init__.py
│   │   ├── allergen_controller.py
│   │   ├── booking_controller.py
│   │   ├── category_controller.py
│   │   ├── dish_controller.py
│   │   ├── menu_controller.py
│   │   ├── menu_detail_controller.py
│   │   ├── restaurant_controller.py
│   │   ├── shift_assignment_controller.py
│   │   ├── shift_table_rel_controller.py
│   │   ├── table_controller.py
│   │   ├── table_rel_controller.py
│   │   ├── test_controller.py
│   │   └── user_controller.py
│   ├── schemas/                   # Esquemas de entrada y salida (Pydantic)
│   │   ├── __init__.py
│   │   ├── enums.py               # Valores fijos (roles, estados de reserva...)
│   │   ├── allergen_schema.py
│   │   ├── booking_schema.py
│   │   ├── category_schema.py
│   │   ├── dish_schema.py
│   │   ├── menu_detail_schema.py
│   │   ├── menu_schema.py
│   │   ├── restaurant_schema.py
│   │   ├── shift_assignment_schema.py
│   │   ├── shift_table_rel_schema.py
│   │   ├── table_rel_schema.py
│   │   ├── table_schema.py
│   │   ├── test_schema.py
│   │   └── user_schema.py
│   ├── models/                    # Modelos de base de datos (SQLAlchemy)
│   │   ├── __init__.py            # Importa TODOS los modelos (lo usa Alembic)
│   │   ├── booking_model.py       # Reservas y relación reserva-mesa
│   │   ├── category_model.py
│   │   ├── dish_model.py          # Platos y alérgenos
│   │   ├── menu_model.py          # Menús y detalle de menú
│   │   ├── restaurant_model.py
│   │   ├── shift_model.py         # Turnos, asignaciones y relación turno-mesa
│   │   ├── table_model.py
│   │   ├── test_model.py
│   │   └── user_model.py
│   ├── core/                      # Configuración central
│   │   ├── __init__.py
│   │   ├── config.py              # Variables de entorno con Pydantic Settings
│   │   ├── database_connection.py # Engine, sesión y Base de SQLAlchemy
│   │   ├── exception_handlers.py  # Convierte errores de BD en respuestas claras
│   │   └── security.py            # (pendiente) contraseñas y tokens
│   ├── internal/                  # Rutas internas de administración (sin endpoints aún)
│   │   ├── __init__.py
│   │   └── admin.py
│   ├── services/                  # Lógica de negocio reutilizable
│   │   ├── __init__.py
│   │   └── item_service.py
│   └── db/
│       ├── __init__.py
│       ├── database.py            # Base + todos los modelos cargados
│       └── migrations/            # Migraciones de Alembic
│           ├── README
│           ├── env.py
│           ├── script.py.mako
│           └── versions/
│               └── f28ae170eecb_create_initial_tables.py
├── seeders/                       # Datos iniciales y de prueba
│   ├── __init__.py
│   ├── factories/
│   │   ├── __init__.py
│   │   └── test_factory.py        # Faker: inventa un registro de la tabla test
│   ├── allergen_seeder.py         # Los 14 alérgenos oficiales (datos fijos)
│   ├── demo_seeder.py             # Restaurante de demo completo (datos fijos)
│   ├── test_seeder.py             # Registros falsos para la tabla test
│   └── run.py                     # Lanzador: python -m seeders.run
├── tests/                         # Tests automáticos (uno por entidad)
│   ├── __init__.py
│   ├── test_allergen.py
│   ├── test_booking.py
│   ├── test_category.py
│   ├── test_dish.py
│   ├── test_errors.py             # Casos de error (datos inválidos, borrados protegidos...)
│   ├── test_main.py
│   ├── test_menu.py
│   ├── test_menu_detail.py
│   ├── test_restaurant.py
│   ├── test_shift_assignment.py
│   ├── test_shift_table_rel.py
│   ├── test_table.py
│   ├── test_table_rel.py
│   ├── test_test.py
│   └── test_user.py
├── .env                           # Variables de entorno (NO se sube a Git)
├── .gitattributes
├── .gitignore
├── alembic.ini                    # Configuración de Alembic
├── requirements.txt
├── README.md
└── run.sh                         # Levanta el servidor (activa .venv o env si existe)
```

> Las carpetas `__pycache__/`, el entorno virtual (`.venv/` o `env/`) y `.env` están en `.gitignore` y no se suben al repositorio.

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

Crea un archivo llamado `.env` en la raíz del proyecto (al lado de `README.md`) con este contenido, y ajusta las credenciales de tu PostgreSQL:

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

> Todos los endpoints se pueden probar desde Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### General
- `GET /` - Mensaje de bienvenida.
- `GET /health/db` - Verifica la conexión con la base de datos PostgreSQL.

### Restaurantes (`/restaurants`)
- `POST /restaurants/` - Crear.
- `GET /restaurants/` - Listar con paginación (`skip`, `limit`).
- `GET /restaurants/{id_rest}` - Obtener por ID.
- `PUT /restaurants/{id_rest}` - Actualizar.
- `DELETE /restaurants/{id_rest}` - Eliminar.

### Usuarios (`/users`)
- `POST /users/` - Crear (requiere un `id_rest_user` válido).
- `GET /users/` - Listar con paginación (`skip`, `limit`).
- `GET /users/{id_user}` - Obtener por ID.
- `PUT /users/{id_user}` - Actualizar.
- `DELETE /users/{id_user}` - Eliminar.

### Categorías (`/categories`)
- `POST /categories/` - Crear.
- `GET /categories/` - Listar con paginación (`skip`, `limit`).
- `GET /categories/{id_cat_rest}` - Obtener por ID.
- `PUT /categories/{id_cat_rest}` - Actualizar.
- `DELETE /categories/{id_cat_rest}` - Eliminar.

### Platos (`/dishes`)
- `POST /dishes/` - Crear.
- `GET /dishes/` - Listar.
- `GET /dishes/{id_dish}` - Obtener por ID.
- `PUT /dishes/{id_dish}` - Actualizar.
- `DELETE /dishes/{id_dish}` - Eliminar.

### Alérgenos (`/allergens`)
- `POST /allergens/` - Crear.
- `GET /allergens/` - Listar.
- `GET /allergens/{id_allergen}` - Obtener por ID.
- `PUT /allergens/{id_allergen}` - Actualizar.
- `DELETE /allergens/{id_allergen}` - Eliminar.

### Menús (`/menus`)
- `POST /menus/` - Crear.
- `GET /menus/` - Listar con paginación (`skip`, `limit`).
- `GET /menus/{id_menu}` - Obtener por ID.
- `PUT /menus/{id_menu}` - Actualizar.
- `DELETE /menus/{id_menu}` - Eliminar.

### Detalle de Menú (`/menu-details`)
- `POST /menu-details/` - Añadir un plato a un menú.
- `GET /menu-details/` - Listar todos los detalles con paginación (`skip`, `limit`).
- `GET /menu-details/menu/{id_menu}` - Ver los platos de un menú concreto.
- `DELETE /menu-details/{id_menu}/{id_dish}` - Quitar un plato de un menú.

### Mesas (`/tables`)
- `POST /tables/` - Crear.
- `GET /tables/` - Listar con paginación (`skip`, `limit`) y filtro opcional `id_rest`.
- `GET /tables/{id_table}` - Obtener por ID.
- `PUT /tables/{id_table}` - Actualizar.
- `DELETE /tables/{id_table}` - Eliminar.

### Reservas (`/bookings`)
- `POST /bookings/` - Crear.
- `GET /bookings/` - Listar con paginación (`skip`, `limit`) y filtros opcionales (`id_rest`, `date_booking`, `state_booking`). Ejemplo: `/bookings/?id_rest=1&date_booking=2026-11-20&state_booking=pendiente`.
- `GET /bookings/{id_booking}` - Obtener por ID.
- `PUT /bookings/{id_booking}` - Actualizar.
- `DELETE /bookings/{id_booking}` - Eliminar.

### Relación Reserva-Mesa (`/table-rels`)
- `POST /table-rels/` - Asignar una mesa a una reserva.
- `GET /table-rels/` - Listar con paginación (`skip`, `limit`) y filtros opcionales (`id_booking`, `id_table`).
- `GET /table-rels/{id_booking}/{id_table}` - Obtener una relación concreta.
- `PUT /table-rels/{id_booking}/{id_table}` - Actualizar (por ejemplo, mover la reserva a otra mesa).
- `DELETE /table-rels/{id_booking}/{id_table}` - Eliminar la relación.

### Asignación de Turnos (`/shift-assignments`)
- `POST /shift-assignments/` - Crear (valida que existan `id_user_assign` e `id_shift_assign`).
- `GET /shift-assignments/` - Listar con paginación (`skip`, `limit`) y filtros opcionales (`id_user`, `id_shift`, `date_assign`).
- `GET /shift-assignments/{id_assign}` - Obtener por ID.
- `PUT /shift-assignments/{id_assign}` - Actualizar.
- `DELETE /shift-assignments/{id_assign}` - Eliminar.

### Relación Turno-Mesa (`/shift-table-rels`)
- `POST /shift-table-rels/` - Crear (valida `id_assign_shift_table_rel` e `id_table_shift_table_rel`).
- `GET /shift-table-rels/` - Listar con paginación (`skip`, `limit`) y filtros opcionales (`id_assign`, `id_table`).
- `GET /shift-table-rels/{id_shift_table_rel}` - Obtener por ID.
- `PUT /shift-table-rels/{id_shift_table_rel}` - Actualizar.
- `DELETE /shift-table-rels/{id_shift_table_rel}` - Eliminar.

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
...
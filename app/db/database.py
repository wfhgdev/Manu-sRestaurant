"""
Punto único de acceso a la base de datos CON todos los modelos cargados.

La conexión en sí está en app/core/database_connection.py.
Este archivo, además, importa app.models para que Base "conozca" todas
las tablas. Lo usa Alembic (app/db/migrations/env.py) para saber qué
tablas tiene que crear o modificar.
"""
from app.core.database_connection import Base, engine, SessionLocal, get_db
import app.models  # noqa: F401  (registra todos los modelos en Base)

__all__ = ["Base", "engine", "SessionLocal", "get_db"]

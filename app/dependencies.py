"""
Dependencias compartidas por varias rutas.

Aquí se agrupan las cosas que muchas rutas necesitan "inyectar" con Depends(),
para no repetirlas en cada archivo de app/routers/.

Ejemplo de uso en una ruta:

    from app.dependencies import DbSession

    @router.get("/")
    def listar(db: DbSession):
        ...
"""
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database_connection import get_db

# Atajo: "una sesión de base de datos" lista para usar en cualquier ruta
DbSession = Annotated[Session, Depends(get_db)]

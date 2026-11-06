"""
Rutas internas de administración (solo para uso del equipo / superadministrador).

Todavía no tiene endpoints. Cuando se añadan, se registra en app/main.py así:

    from app.internal import admin
    app.include_router(admin.router)
"""
from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin"])

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.core.database_connection import engine
from app.routers import (
    test_routes,
    user_routes,
    restaurant_routes,
    shift_assignment_routes,
    menu_routes,
    booking_routes,
    table_routes,
    allergen_routes,
)

# Las tablas ya NO se crean aquí con Base.metadata.create_all().
# Ahora las crea Alembic con: alembic upgrade head

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)

app.include_router(test_routes.router)
app.include_router(user_routes.router)
app.include_router(restaurant_routes.router)
app.include_router(allergen_routes.router)
app.include_router(shift_assignment_routes.router)
app.include_router(menu_routes.router)
app.include_router(table_routes.router)
app.include_router(booking_routes.router)


@app.get("/")
async def root():
    return "API template"


@app.get("/health/db", tags=["Health"])
def check_database():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"message": "Conexión a la base de datos exitosa"}

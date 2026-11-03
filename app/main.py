from fastapi import FastAPI
from app.core.config import settings
from app.core.database_connection import engine, Base
from sqlalchemy import text
import app.models  # noqa: F401
from app.api import test_routes, user_routes

# Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION
)

app.include_router(test_routes.router)
app.include_router(user_routes.router)


@app.get("/health/db", tags=["Health"])
def check_database():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"message": "Conexión a la base de datos exitosa"}

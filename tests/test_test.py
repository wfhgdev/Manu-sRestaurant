import uuid

from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.main import app
from app.core.database_connection import SessionLocal
from app.models.test_model import TestModel

client = TestClient(app)


def test_read_test_route():
    response = client.get("/test/")
    assert response.status_code == 200
    assert response.json() == {"message": "Test route"}


def test_create_test_and_duplicate():
    name = f"test_{uuid.uuid4().hex[:8]}"

    try:
        # Crear
        response = client.post("/test/", json={"test_name": name, "test_type": "unit"})
        assert response.status_code == 201
        assert response.json()["test_name"] == name

        # Nombre repetido: no se permite
        response = client.post("/test/", json={"test_name": name, "test_type": "e2e"})
        assert response.status_code == 400

        # Faltan datos
        assert client.post("/test/", json={"test_name": "solo_nombre"}).status_code == 422
    finally:
        # La tabla test no tiene ruta para borrar: se limpia directamente
        db = SessionLocal()
        db.execute(delete(TestModel).where(TestModel.test_name == name))
        db.commit()
        db.close()

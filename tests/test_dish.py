from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import text
from app.core.database_connection import engine

client = TestClient(app)


def test_get_dishes():
    response = client.get("/dishes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_dish_not_found():
    response = client.get("/dishes/999999")
    assert response.status_code == 404


def test_dish_crud_flow():
    conn = engine.connect()
    restaurant_id = conn.execute(
        text("SELECT id_rest FROM restaurant LIMIT 1")
    ).scalar()
    conn.close()

    assert restaurant_id is not None

    category_id = None
    dish_id = None

    try:
        # Crear categoría de prueba directamente en la base de datos
        with engine.begin() as conn:
            category_id = conn.execute(
                text("""
                    INSERT INTO cat_rest (id_rest_cat_rest, name_cat_rest)
                    VALUES (:restaurant_id, :name)
                    RETURNING id_cat_rest
                """),
                {
                    "restaurant_id": restaurant_id,
                    "name": "Categoría de prueba"
                }
            ).scalar()

        # Crear plato
        response = client.post("/dishes/", json={
            "id_rest_dish": restaurant_id,
            "id_cat_dish": category_id,
            "name_dish": "Plato de prueba",
            "desc_dish": "Descripción de prueba",
            "price_dish": "12.50",
            "state_dish": True,
            "allergen_ids": []
        })

        assert response.status_code == 201
        dish_id = response.json()["id_dish"]

        # Consultar
        response = client.get(f"/dishes/{dish_id}")
        assert response.status_code == 200
        assert response.json()["name_dish"] == "Plato de prueba"

        # Actualizar
        response = client.put(f"/dishes/{dish_id}", json={
            "name_dish": "Plato modificado",
            "price_dish": "15.50"
        })

        assert response.status_code == 200
        assert response.json()["name_dish"] == "Plato modificado"

        # Eliminar
        response = client.delete(f"/dishes/{dish_id}")
        assert response.status_code == 200

        # Comprobar que ya no existe
        response = client.get(f"/dishes/{dish_id}")
        assert response.status_code == 404

    finally:
        if dish_id is not None:
            client.delete(f"/dishes/{dish_id}")

        if category_id is not None:
            with engine.begin() as conn:
                conn.execute(
                    text("DELETE FROM cat_rest WHERE id_cat_rest = :id"),
                    {"id": category_id}
                )
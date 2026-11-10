import uuid

from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import text
from app.core.database_connection import engine

client = TestClient(app)


def create_temp_restaurant(name: str) -> int:
    # Restaurante temporal (CIF aleatorio para no repetir)
    return client.post("/restaurants/", json={
        "cif_rest": f"T{uuid.uuid4().hex[:8].upper()}",
        "name_rest": name,
    }).json()["id_rest"]


def create_category(restaurant_id: int, name: str) -> int:
    # No hay rutas de categorías: se crea directamente en la base de datos
    with engine.begin() as conn:
        return conn.execute(
            text("""
                INSERT INTO cat_rest (id_rest_cat_rest, name_cat_rest, state_cat_rest)
                VALUES (:restaurant_id, :name, true)
                RETURNING id_cat_rest
            """),
            {"restaurant_id": restaurant_id, "name": name}
        ).scalar()


def test_get_dishes():
    response = client.get("/dishes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_dish_not_found():
    response = client.get("/dishes/999999")
    assert response.status_code == 404


def test_dish_crud_flow():
    restaurant_id = create_temp_restaurant("Restaurante test platos")
    dish_id = None

    try:
        # Crear categoría de prueba directamente en la base de datos
        category_id = create_category(restaurant_id, "Categoría de prueba")

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

        # Al borrar el restaurante se borran también sus categorías y platos
        client.delete(f"/restaurants/{restaurant_id}")


def test_dish_validation_errors():
    restaurant_id = create_temp_restaurant("Restaurante test errores platos")
    other_restaurant_id = create_temp_restaurant("Otro restaurante test platos")

    try:
        category_id = create_category(restaurant_id, "Categoría A")
        other_category_id = create_category(other_restaurant_id, "Categoría B")

        dish = {
            "id_rest_dish": restaurant_id,
            "id_cat_dish": category_id,
            "name_dish": "Plato test",
            "price_dish": "10.00",
        }

        # Restaurante que no existe
        response = client.post("/dishes/", json={**dish, "id_rest_dish": 999999})
        assert response.status_code == 404

        # Categoría que no existe
        response = client.post("/dishes/", json={**dish, "id_cat_dish": 999999})
        assert response.status_code == 404

        # Categoría de otro restaurante
        response = client.post("/dishes/", json={**dish, "id_cat_dish": other_category_id})
        assert response.status_code == 400

        # Alérgeno que no existe
        response = client.post("/dishes/", json={**dish, "allergen_ids": [999999]})
        assert response.status_code == 404

        # Precio negativo y nombre vacío
        assert client.post("/dishes/", json={**dish, "price_dish": "-1"}).status_code == 422
        assert client.post("/dishes/", json={**dish, "name_dish": ""}).status_code == 422

        # Actualizar un plato que no existe
        assert client.put("/dishes/999999", json={"name_dish": "X"}).status_code == 404

        # Borrar un plato que no existe
        assert client.delete("/dishes/999999").status_code == 404
    finally:
        client.delete(f"/restaurants/{restaurant_id}")
        client.delete(f"/restaurants/{other_restaurant_id}")

import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_temp_restaurant(name: str) -> int:
    # Restaurante temporal (CIF aleatorio para no repetir)
    return client.post("/restaurants/", json={
        "cif_rest": f"T{uuid.uuid4().hex[:8].upper()}",
        "name_rest": name,
    }).json()["id_rest"]


def test_get_categories():
    response = client.get("/categories/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_category_not_found():
    response = client.get("/categories/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Categoría con id_cat_rest 999999 no encontrada"}


def test_create_category_errors():
    # Restaurante que no existe
    response = client.post("/categories/", json={"id_rest_cat_rest": 999999, "name_cat_rest": "Postres"})
    assert response.status_code == 404
    # Nombre vacío o demasiado largo
    assert client.post("/categories/", json={"id_rest_cat_rest": 1, "name_cat_rest": ""}).status_code == 422
    assert client.post("/categories/", json={"id_rest_cat_rest": 1, "name_cat_rest": "X" * 101}).status_code == 422


def test_update_and_delete_category_not_found():
    assert client.put("/categories/999999", json={"name_cat_rest": "X"}).status_code == 404
    assert client.delete("/categories/999999").status_code == 404


def test_category_crud_flow():
    id_rest = create_temp_restaurant("Restaurante test categorías")
    other_rest = create_temp_restaurant("Otro restaurante test categorías")

    try:
        # Crear
        response = client.post("/categories/", json={"id_rest_cat_rest": id_rest, "name_cat_rest": "Entrantes"})
        assert response.status_code == 201
        category = response.json()
        assert category["state_cat_rest"] is True

        # Nombre repetido en el mismo restaurante: no se permite
        response = client.post("/categories/", json={"id_rest_cat_rest": id_rest, "name_cat_rest": "Entrantes"})
        assert response.status_code == 400

        # El mismo nombre en otro restaurante sí se permite
        other = client.post("/categories/", json={"id_rest_cat_rest": other_rest, "name_cat_rest": "Entrantes"})
        assert other.status_code == 201

        # Consultar y actualizar
        assert client.get(f"/categories/{category['id_cat_rest']}").status_code == 200
        response = client.put(f"/categories/{category['id_cat_rest']}", json={"name_cat_rest": "Para picar"})
        assert response.status_code == 200
        assert response.json()["name_cat_rest"] == "Para picar"

        # Borrar
        response = client.delete(f"/categories/{category['id_cat_rest']}")
        assert response.status_code == 200
        assert client.get(f"/categories/{category['id_cat_rest']}").status_code == 404
    finally:
        client.delete(f"/restaurants/{id_rest}")
        client.delete(f"/restaurants/{other_rest}")


def test_category_with_dishes_is_protected():
    id_rest = create_temp_restaurant("Restaurante test categoría con platos")
    other_rest = create_temp_restaurant("Otro restaurante test categoría con platos")

    try:
        category = client.post("/categories/", json={"id_rest_cat_rest": id_rest, "name_cat_rest": "Postres"}).json()
        dish = client.post("/dishes/", json={
            "id_rest_dish": id_rest,
            "id_cat_dish": category["id_cat_rest"],
            "name_dish": "Flan",
            "price_dish": "4.50",
        }).json()

        # No se puede borrar: se borrarían también sus platos
        response = client.delete(f"/categories/{category['id_cat_rest']}")
        assert response.status_code == 400
        assert client.get(f"/dishes/{dish['id_dish']}").status_code == 200

        # No se puede mover a otro restaurante: sus platos son de este
        response = client.put(f"/categories/{category['id_cat_rest']}", json={"id_rest_cat_rest": other_rest})
        assert response.status_code == 400

        # Desactivarla sí se permite
        response = client.put(f"/categories/{category['id_cat_rest']}", json={"state_cat_rest": False})
        assert response.status_code == 200
        assert response.json()["state_cat_rest"] is False
    finally:
        client.delete(f"/restaurants/{id_rest}")
        client.delete(f"/restaurants/{other_rest}")

import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_menus():
    response = client.get("/menus/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_menu_not_found():
    response = client.get("/menus/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Menú con id_menu 999999 no encontrado"}


def test_create_menu_restaurant_not_found():
    response = client.post("/menus/", json={
        "id_rest_menu": 999999,
        "name_menu": "Menú test",
        "price_menu": "12.50",
    })
    assert response.status_code == 404


def test_create_menu_invalid_data():
    # Precio negativo
    response = client.post("/menus/", json={
        "id_rest_menu": 1,
        "name_menu": "Menú test",
        "price_menu": "-1",
    })
    assert response.status_code == 422

    # Nombre vacío
    response = client.post("/menus/", json={
        "id_rest_menu": 1,
        "name_menu": "",
        "price_menu": "10",
    })
    assert response.status_code == 422


def test_menu_crud_flow():
    # Restaurante temporal solo para este test
    restaurant = client.post("/restaurants/", json={
        "cif_rest": f"T{uuid.uuid4().hex[:8].upper()}",
        "name_rest": "Restaurante test menús",
    }).json()
    id_rest = restaurant["id_rest"]

    try:
        # Crear
        response = client.post("/menus/", json={
            "id_rest_menu": id_rest,
            "name_menu": "Menú del día",
            "price_menu": "13.90",
        })
        assert response.status_code == 201
        menu = response.json()
        assert menu["state_menu"] is True

        # Consultar
        response = client.get(f"/menus/{menu['id_menu']}")
        assert response.status_code == 200
        assert response.json()["name_menu"] == "Menú del día"

        # Actualizar
        response = client.put(f"/menus/{menu['id_menu']}", json={"price_menu": "14.50", "state_menu": False})
        assert response.status_code == 200
        assert response.json()["price_menu"] == "14.50"
        assert response.json()["state_menu"] is False

        # Actualizar con un restaurante que no existe
        response = client.put(f"/menus/{menu['id_menu']}", json={"id_rest_menu": 999999})
        assert response.status_code == 404

        # Borrar
        response = client.delete(f"/menus/{menu['id_menu']}")
        assert response.status_code == 200
        assert client.get(f"/menus/{menu['id_menu']}").status_code == 404

        # Borrar otra vez: ya no existe
        assert client.delete(f"/menus/{menu['id_menu']}").status_code == 404
    finally:
        client.delete(f"/restaurants/{id_rest}")

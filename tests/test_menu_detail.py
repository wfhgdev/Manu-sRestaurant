import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_restaurant_with_menu_and_dish(name: str) -> dict:
    # Restaurante temporal con una categoría, un plato y un menú
    id_rest = client.post("/restaurants/", json={
        "cif_rest": f"T{uuid.uuid4().hex[:8].upper()}",
        "name_rest": name,
    }).json()["id_rest"]
    id_cat = client.post("/categories/", json={"id_rest_cat_rest": id_rest, "name_cat_rest": "Principales"}).json()["id_cat_rest"]
    id_dish = client.post("/dishes/", json={
        "id_rest_dish": id_rest, "id_cat_dish": id_cat, "name_dish": "Paella", "price_dish": "16.50",
    }).json()["id_dish"]
    id_menu = client.post("/menus/", json={
        "id_rest_menu": id_rest, "name_menu": "Menú del día", "price_menu": "13.90",
    }).json()["id_menu"]
    return {"id_rest": id_rest, "id_dish": id_dish, "id_menu": id_menu}


def test_get_menu_details():
    response = client.get("/menu-details/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_menu_detail_not_found():
    # Menú que no existe
    assert client.get("/menu-details/menu/999999").status_code == 404
    # Quitar un plato que no está en el menú
    assert client.delete("/menu-details/999999/999999").status_code == 404


def test_menu_detail_flow():
    data = create_restaurant_with_menu_and_dish("Restaurante test detalle menú")
    other = create_restaurant_with_menu_and_dish("Otro restaurante test detalle menú")

    try:
        payload = {"id_menu_det": data["id_menu"], "id_dish_det": data["id_dish"]}

        # Añadir el plato al menú
        response = client.post("/menu-details/", json=payload)
        assert response.status_code == 201
        assert response.json() == payload

        # Añadirlo otra vez: no se permite
        assert client.post("/menu-details/", json=payload).status_code == 400

        # Plato de otro restaurante: no se permite
        response = client.post("/menu-details/", json={"id_menu_det": data["id_menu"], "id_dish_det": other["id_dish"]})
        assert response.status_code == 400

        # Menú o plato que no existen
        assert client.post("/menu-details/", json={"id_menu_det": 999999, "id_dish_det": data["id_dish"]}).status_code == 404
        assert client.post("/menu-details/", json={"id_menu_det": data["id_menu"], "id_dish_det": 999999}).status_code == 404

        # Listar los platos del menú
        response = client.get(f"/menu-details/menu/{data['id_menu']}")
        assert [d["id_dish_det"] for d in response.json()] == [data["id_dish"]]

        # Un plato que está en un menú no se puede borrar (desaparecería del menú sin avisar)
        assert client.delete(f"/dishes/{data['id_dish']}").status_code == 400

        # Quitar el plato del menú
        response = client.delete(f"/menu-details/{data['id_menu']}/{data['id_dish']}")
        assert response.status_code == 200
        assert client.get(f"/menu-details/menu/{data['id_menu']}").json() == []

        # Ahora el plato sí se puede borrar
        assert client.delete(f"/dishes/{data['id_dish']}").status_code == 200
    finally:
        client.delete(f"/restaurants/{data['id_rest']}")
        client.delete(f"/restaurants/{other['id_rest']}")

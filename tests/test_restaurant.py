import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def random_cif() -> str:
    # CIF aleatorio para que los tests no choquen con datos existentes
    return f"T{uuid.uuid4().hex[:8].upper()}"


def test_get_restaurants():
    response = client.get("/restaurants/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_restaurant_not_found():
    response = client.get("/restaurants/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Restaurante con id_rest 999999 no encontrado"}


def test_create_restaurant_invalid_data():
    # Falta el nombre
    assert client.post("/restaurants/", json={"cif_rest": random_cif()}).status_code == 422
    # CIF más largo de lo permitido (20 caracteres)
    assert client.post("/restaurants/", json={"cif_rest": "X" * 21, "name_rest": "R"}).status_code == 422
    # Nombre vacío
    assert client.post("/restaurants/", json={"cif_rest": random_cif(), "name_rest": ""}).status_code == 422


def test_update_and_delete_restaurant_not_found():
    assert client.put("/restaurants/999999", json={"name_rest": "X"}).status_code == 404
    assert client.delete("/restaurants/999999").status_code == 404


def test_restaurant_crud_flow():
    cif = random_cif()
    other_cif = random_cif()

    # Crear
    response = client.post("/restaurants/", json={
        "cif_rest": cif,
        "name_rest": "Restaurante test",
        "address_rest": "Calle Test 1",
        "tel_rest": "968000000",
    })
    assert response.status_code == 201
    restaurant = response.json()
    id_rest = restaurant["id_rest"]

    other = client.post("/restaurants/", json={"cif_rest": other_cif, "name_rest": "Otro"}).json()

    try:
        # CIF repetido
        response = client.post("/restaurants/", json={"cif_rest": cif, "name_rest": "Duplicado"})
        assert response.status_code == 400

        # Consultar
        response = client.get(f"/restaurants/{id_rest}")
        assert response.status_code == 200
        assert response.json()["name_rest"] == "Restaurante test"

        # Listar con paginación
        response = client.get("/restaurants/?skip=0&limit=1000")
        assert any(r["id_rest"] == id_rest for r in response.json())

        # Actualizar
        response = client.put(f"/restaurants/{id_rest}", json={"name_rest": "Restaurante modificado"})
        assert response.status_code == 200
        assert response.json()["name_rest"] == "Restaurante modificado"

        # Actualizar a un CIF que ya usa otro restaurante
        response = client.put(f"/restaurants/{id_rest}", json={"cif_rest": other_cif})
        assert response.status_code == 400

        # Borrar
        response = client.delete(f"/restaurants/{id_rest}")
        assert response.status_code == 200
        assert client.get(f"/restaurants/{id_rest}").status_code == 404
    finally:
        client.delete(f"/restaurants/{id_rest}")
        client.delete(f"/restaurants/{other['id_rest']}")

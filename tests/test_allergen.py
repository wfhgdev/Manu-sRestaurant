
import uuid

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_allergens():
    response = client.get("/allergens/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_allergen_not_found():
    response = client.get("/allergens/999999")
    assert response.status_code == 404


def test_allergen_crud_flow():
    # Crear
    response = client.post("/allergens/", json={
        "name_allergen": "Alérgeno de prueba"
    })
    assert response.status_code == 201

    allergen = response.json()
    id_allergen = allergen["id_allergen"]

    try:
        # Consultar
        response = client.get(f"/allergens/{id_allergen}")
        assert response.status_code == 200

        # Actualizar
        response = client.put(f"/allergens/{id_allergen}", json={
            "name_allergen": "Alérgeno modificado"
        })
        assert response.status_code == 200
        assert response.json()["name_allergen"] == "Alérgeno modificado"

        # Eliminar
        response = client.delete(f"/allergens/{id_allergen}")
        assert response.status_code == 200

        # Comprobar que ya no existe
        response = client.get(f"/allergens/{id_allergen}")
        assert response.status_code == 404

    finally:
        # Evitar dejar datos de prueba si algo falla
        client.delete(f"/allergens/{id_allergen}")

def test_create_allergen_invalid_name():
    # Nombre vacío
    assert client.post("/allergens/", json={"name_allergen": ""}).status_code == 422
    # Nombre más largo de lo permitido (100 caracteres)
    assert client.post("/allergens/", json={"name_allergen": "X" * 101}).status_code == 422


def test_allergen_duplicated_name():
    name = f"Alérgeno único {uuid.uuid4().hex[:6]}"
    first = client.post("/allergens/", json={"name_allergen": name}).json()
    other = client.post("/allergens/", json={"name_allergen": name + " otro"}).json()

    try:
        # Mismo nombre (aunque cambien mayúsculas): no se permite
        response = client.post("/allergens/", json={"name_allergen": name.upper()})
        assert response.status_code == 400

        # Cambiar el nombre de otro alérgeno a uno que ya existe
        response = client.put(f"/allergens/{other['id_allergen']}", json={"name_allergen": name})
        assert response.status_code == 400

        # Mantener su propio nombre sí se permite
        response = client.put(f"/allergens/{first['id_allergen']}", json={"name_allergen": name})
        assert response.status_code == 200
    finally:
        client.delete(f"/allergens/{first['id_allergen']}")
        client.delete(f"/allergens/{other['id_allergen']}")


def test_update_and_delete_allergen_not_found():
    assert client.put("/allergens/999999", json={"name_allergen": "X"}).status_code == 404
    assert client.delete("/allergens/999999").status_code == 404

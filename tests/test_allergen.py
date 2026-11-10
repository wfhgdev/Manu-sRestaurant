
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
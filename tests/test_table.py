import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_tables():
    response = client.get("/tables/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_table_not_found():
    response = client.get("/tables/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Mesa con id_table 999999 no encontrada"}


def test_create_table_invalid_capacity():
    response = client.post("/tables/", json={
        "id_rest_table": 1,
        "name_table": "Mesa X",
        "cap_table": 0,
        "location_table": "interior",
    })
    assert response.status_code == 422


def test_create_table_restaurant_not_found():
    response = client.post("/tables/", json={
        "id_rest_table": 999999,
        "name_table": "Mesa X",
        "cap_table": 4,
        "location_table": "interior",
    })
    assert response.status_code == 404


def test_table_crud_flow():
    # Restaurante temporal solo para este test (CIF aleatorio para no repetir)
    restaurant = client.post("/restaurants/", json={
        "cif_rest": f"T{uuid.uuid4().hex[:8].upper()}",
        "name_rest": "Restaurante test mesas",
    }).json()
    id_rest = restaurant["id_rest"]

    try:
        # Crear
        response = client.post("/tables/", json={
            "id_rest_table": id_rest,
            "name_table": "Mesa 1",
            "cap_table": 4,
            "location_table": "terraza",
        })
        assert response.status_code == 201
        table = response.json()
        assert table["state_table"] is True

        # Nombre repetido en el mismo restaurante
        response = client.post("/tables/", json={
            "id_rest_table": id_rest,
            "name_table": "Mesa 1",
            "cap_table": 2,
            "location_table": "interior",
        })
        assert response.status_code == 400

        # Filtrar por restaurante
        response = client.get(f"/tables/?id_rest={id_rest}")
        assert [t["id_table"] for t in response.json()] == [table["id_table"]]

        # Actualizar
        response = client.put(f"/tables/{table['id_table']}", json={"cap_table": 6, "state_table": False})
        assert response.status_code == 200
        assert response.json()["cap_table"] == 6
        assert response.json()["state_table"] is False

        # Borrar
        response = client.delete(f"/tables/{table['id_table']}")
        assert response.status_code == 200
        assert client.get(f"/tables/{table['id_table']}").status_code == 404
    finally:
        client.delete(f"/restaurants/{id_rest}")

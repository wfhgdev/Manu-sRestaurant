import uuid
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_shifts():
    response = client.get("/shifts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_shift_not_found():
    response = client.get("/shifts/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Turno con id_shift 999999 no encontrado"}


def test_create_shift_restaurant_not_found():
    response = client.post("/shifts/", json={
        "id_rest_shift": 999999,
        "name_shift": "mañana",
        "open_time_shift": "12:00:00",
        "close_time_shift": "16:30:00",
    })
    assert response.status_code == 404


def test_create_shift_same_open_close_time():
    response = client.post("/shifts/", json={
        "id_rest_shift": 1,
        "name_shift": "mañana",
        "open_time_shift": "12:00:00",
        "close_time_shift": "12:00:00",
    })
    assert response.status_code == 400


def test_shift_crud_flow():
    # Restaurante temporal solo para este test (CIF aleatorio para no colisionar)
    cif = f"T{uuid.uuid4().hex[:8].upper()}"
    restaurant_res = client.post("/restaurants/", json={
        "cif_rest": cif,
        "name_rest": "Restaurante Test Turnos",
    })
    assert restaurant_res.status_code == 201
    id_rest = restaurant_res.json()["id_rest"]

    try:
        # 1. Crear turno
        response = client.post("/shifts/", json={
            "id_rest_shift": id_rest,
            "name_shift": "mañana",
            "open_time_shift": "12:00:00",
            "close_time_shift": "16:30:00",
        })
        assert response.status_code == 201
        shift = response.json()
        id_shift = shift["id_shift"]
        assert shift["name_shift"] == "mañana"
        assert shift["id_rest_shift"] == id_rest

        # 2. Nombre de turno duplicado en el mismo restaurante
        dup_response = client.post("/shifts/", json={
            "id_rest_shift": id_rest,
            "name_shift": "mañana",
            "open_time_shift": "13:00:00",
            "close_time_shift": "17:00:00",
        })
        assert dup_response.status_code == 400

        # 3. Obtener por ID
        get_response = client.get(f"/shifts/{id_shift}")
        assert get_response.status_code == 200
        assert get_response.json()["id_shift"] == id_shift

        # 4. Filtrar por restaurante y nombre de turno
        filter_response = client.get(f"/shifts/?id_rest={id_rest}&name_shift=mañana")
        assert filter_response.status_code == 200
        assert [s["id_shift"] for s in filter_response.json()] == [id_shift]

        # 5. Actualizar turno
        update_response = client.put(f"/shifts/{id_shift}", json={
            "open_time_shift": "11:30:00",
            "close_time_shift": "17:00:00",
        })
        assert update_response.status_code == 200
        assert update_response.json()["open_time_shift"] == "11:30:00"
        assert update_response.json()["close_time_shift"] == "17:00:00"

        # 6. Borrar turno
        delete_response = client.delete(f"/shifts/{id_shift}")
        assert delete_response.status_code == 200
        assert client.get(f"/shifts/{id_shift}").status_code == 404
    finally:
        client.delete(f"/restaurants/{id_rest}")


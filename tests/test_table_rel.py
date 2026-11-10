import uuid
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

MANANA = (date.today() + timedelta(days=1)).isoformat()


def test_get_table_rels():
    response = client.get("/table-rels/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_table_rel_not_found():
    response = client.get("/table-rels/999999/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "La mesa 999999 no está asignada a la reserva 999999"}


def test_create_table_rel_booking_not_found():
    response = client.post("/table-rels/", json={
        "id_booking_table_rel": 999999,
        "id_table_table_rel": 1,
    })
    assert response.status_code == 404


def test_table_rel_crud_flow():
    # Restaurante temporal con 2 mesas y 2 reservas, solo para este test
    restaurant = client.post("/restaurants/", json={
        "cif_rest": f"T{uuid.uuid4().hex[:8].upper()}",
        "name_rest": "Restaurante test mesas por reserva",
    }).json()
    id_rest = restaurant["id_rest"]

    try:
        mesa_1 = client.post("/tables/", json={
            "id_rest_table": id_rest, "name_table": "Mesa 1", "cap_table": 4, "location_table": "interior",
        }).json()["id_table"]
        mesa_2 = client.post("/tables/", json={
            "id_rest_table": id_rest, "name_table": "Mesa 2", "cap_table": 4, "location_table": "terraza",
        }).json()["id_table"]
        reserva_14h = client.post("/bookings/", json={
            "id_rest_booking": id_rest, "name_client_booking": "Cliente 14h",
            "date_booking": MANANA, "start_time_booking": "14:00", "qty_booking": 4,
        }).json()["id_booking"]
        reserva_15h = client.post("/bookings/", json={
            "id_rest_booking": id_rest, "name_client_booking": "Cliente 15h",
            "date_booking": MANANA, "start_time_booking": "15:00", "qty_booking": 2,
        }).json()["id_booking"]

        # Asignar la Mesa 1 a la reserva de las 14:00
        response = client.post("/table-rels/", json={
            "id_booking_table_rel": reserva_14h, "id_table_table_rel": mesa_1,
        })
        assert response.status_code == 201
        assert response.json() == {"id_booking_table_rel": reserva_14h, "id_table_table_rel": mesa_1}

        # Repetir la misma asignación: no se permite
        response = client.post("/table-rels/", json={
            "id_booking_table_rel": reserva_14h, "id_table_table_rel": mesa_1,
        })
        assert response.status_code == 400

        # La Mesa 1 está ocupada a las 15:00 (menos de 2 horas después)
        response = client.post("/table-rels/", json={
            "id_booking_table_rel": reserva_15h, "id_table_table_rel": mesa_1,
        })
        assert response.status_code == 400

        # Filtrar las mesas de una reserva y ver una relación concreta
        response = client.get(f"/table-rels/?id_booking={reserva_14h}")
        assert [r["id_table_table_rel"] for r in response.json()] == [mesa_1]
        assert client.get(f"/table-rels/{reserva_14h}/{mesa_1}").status_code == 200

        # Cambiar la reserva de las 14:00 a la Mesa 2
        response = client.put(f"/table-rels/{reserva_14h}/{mesa_1}", json={"id_table_table_rel": mesa_2})
        assert response.status_code == 200
        assert response.json()["id_table_table_rel"] == mesa_2

        # Ahora la Mesa 1 está libre para la reserva de las 15:00
        response = client.post("/table-rels/", json={
            "id_booking_table_rel": reserva_15h, "id_table_table_rel": mesa_1,
        })
        assert response.status_code == 201

        # Quitar una mesa de una reserva
        response = client.delete(f"/table-rels/{reserva_15h}/{mesa_1}")
        assert response.status_code == 200
        assert client.get(f"/table-rels/{reserva_15h}/{mesa_1}").status_code == 404
    finally:
        client.delete(f"/restaurants/{id_rest}")

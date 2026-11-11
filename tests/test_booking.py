import uuid
from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

MANANA = (date.today() + timedelta(days=1)).isoformat()
AYER = (date.today() - timedelta(days=1)).isoformat()


def test_get_bookings():
    response = client.get("/bookings/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_booking_not_found():
    response = client.get("/bookings/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Reserva con id_booking 999999 no encontrada"}


def test_create_booking_invalid_qty():
    response = client.post("/bookings/", json={
        "id_rest_booking": 1,
        "name_client_booking": "Cliente test",
        "date_booking": MANANA,
        "start_time_booking": "21:00",
        "qty_booking": 0,
    })
    assert response.status_code == 422


def test_create_booking_restaurant_not_found():
    response = client.post("/bookings/", json={
        "id_rest_booking": 999999,
        "name_client_booking": "Cliente test",
        "date_booking": MANANA,
        "start_time_booking": "21:00",
        "qty_booking": 2,
    })
    assert response.status_code == 404


def test_booking_crud_flow():
    # Restaurante temporal solo para este test (CIF aleatorio para no repetir)
    restaurant = client.post("/restaurants/", json={
        "cif_rest": f"T{uuid.uuid4().hex[:8].upper()}",
        "name_rest": "Restaurante test reservas",
    }).json()
    id_rest = restaurant["id_rest"]

    try:
        # Fecha pasada: no se permite
        response = client.post("/bookings/", json={
            "id_rest_booking": id_rest,
            "name_client_booking": "Cliente test",
            "date_booking": AYER,
            "start_time_booking": "21:00",
            "qty_booking": 2,
        })
        assert response.status_code == 400

        # Crear (sin estado: nace como "pendiente")
        response = client.post("/bookings/", json={
            "id_rest_booking": id_rest,
            "name_client_booking": "Cliente test",
            "date_booking": MANANA,
            "start_time_booking": "21:00",
            "qty_booking": 2,
        })
        assert response.status_code == 201
        booking = response.json()
        assert booking["state_booking"] == "pendiente"
        assert "timestamp_booking" in booking

        # Filtrar por restaurante y estado
        response = client.get(f"/bookings/?id_rest={id_rest}&state_booking=pendiente")
        assert [b["id_booking"] for b in response.json()] == [booking["id_booking"]]

        # Confirmar y cambiar el número de personas
        response = client.put(f"/bookings/{booking['id_booking']}", json={
            "state_booking": "confirmada",
            "qty_booking": 4,
        })
        assert response.status_code == 200
        assert response.json()["state_booking"] == "confirmada"
        assert response.json()["qty_booking"] == 4

        # Borrar
        response = client.delete(f"/bookings/{booking['id_booking']}")
        assert response.status_code == 200
        assert client.get(f"/bookings/{booking['id_booking']}").status_code == 404
    finally:
        client.delete(f"/restaurants/{id_rest}")


def test_move_booking_to_occupied_time():
    # Restaurante temporal con una mesa y dos reservas el mismo día (14:00 y 18:00) en esa mesa
    id_rest = client.post("/restaurants/", json={
        "cif_rest": f"T{uuid.uuid4().hex[:8].upper()}",
        "name_rest": "Restaurante test mover reservas",
    }).json()["id_rest"]

    try:
        id_table = client.post("/tables/", json={
            "id_rest_table": id_rest, "name_table": "Mesa 1", "cap_table": 4, "location_table": "interior",
        }).json()["id_table"]
        booking_14 = client.post("/bookings/", json={
            "id_rest_booking": id_rest, "name_client_booking": "Cliente 14h",
            "date_booking": MANANA, "start_time_booking": "14:00", "qty_booking": 2,
        }).json()["id_booking"]
        booking_18 = client.post("/bookings/", json={
            "id_rest_booking": id_rest, "name_client_booking": "Cliente 18h",
            "date_booking": MANANA, "start_time_booking": "18:00", "qty_booking": 2,
        }).json()["id_booking"]
        for id_booking in (booking_14, booking_18):
            assert client.post("/table-rels/", json={
                "id_booking_table_rel": id_booking, "id_table_table_rel": id_table,
            }).status_code == 201

        # Mover la de las 18:00 a las 14:30: la mesa ya está ocupada a esa hora
        response = client.put(f"/bookings/{booking_18}", json={"start_time_booking": "14:30"})
        assert response.status_code == 400

        # Moverla a las 20:00 sí se permite
        response = client.put(f"/bookings/{booking_18}", json={"start_time_booking": "20:00"})
        assert response.status_code == 200

        # Cancelar la de las 14:00 y mover la otra a las 14:30: ahora sí está libre
        assert client.put(f"/bookings/{booking_14}", json={"state_booking": "cancelada"}).status_code == 200
        assert client.put(f"/bookings/{booking_18}", json={"start_time_booking": "14:30"}).status_code == 200

        # Reactivar la cancelada: pisaría a la otra, no se permite
        response = client.put(f"/bookings/{booking_14}", json={"state_booking": "pendiente"})
        assert response.status_code == 400
    finally:
        client.delete(f"/restaurants/{id_rest}")

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

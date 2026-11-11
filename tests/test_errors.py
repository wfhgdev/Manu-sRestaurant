"""
Tests de los manejadores de errores globales (app/core/exception_handlers.py).

Comprueban que la API responde con un error claro (400) en lugar de
romperse con un "500 Internal Server Error".
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

NUMERO_ENORME = 99999999999  # más grande de lo que admite un INTEGER de PostgreSQL


@pytest.mark.parametrize("ruta", [
    f"/restaurants/{NUMERO_ENORME}",
    f"/users/{NUMERO_ENORME}",
    f"/menus/{NUMERO_ENORME}",
    f"/allergens/{NUMERO_ENORME}",
    f"/dishes/{NUMERO_ENORME}",
    f"/tables/{NUMERO_ENORME}",
    f"/bookings/{NUMERO_ENORME}",
    f"/table-rels/{NUMERO_ENORME}/{NUMERO_ENORME}",
    f"/shift-assignments/{NUMERO_ENORME}",
    f"/shift-table-rels/{NUMERO_ENORME}",
    f"/categories/{NUMERO_ENORME}",
    f"/menu-details/menu/{NUMERO_ENORME}",
])
def test_id_demasiado_grande(ruta):
    response = client.get(ruta)
    assert response.status_code == 400
    assert response.json() == {"detail": "Algún número enviado es demasiado grande para la base de datos"}


@pytest.mark.parametrize("ruta", [
    "/restaurants/?skip=-1",
    "/users/?limit=-1",
    "/menus/?skip=-5",
    "/tables/?limit=-1",
    "/bookings/?skip=-1",
    "/table-rels/?limit=-1",
    "/shift-assignments/?skip=-1",
    "/shift-table-rels/?limit=-1",
    "/categories/?skip=-1",
    "/menu-details/?limit=-1",
])
def test_paginacion_negativa(ruta):
    response = client.get(ruta)
    assert response.status_code == 400
    assert response.json() == {"detail": "Los parámetros skip y limit no pueden ser negativos"}


def test_numero_enorme_en_el_body():
    response = client.post("/bookings/", json={
        "id_rest_booking": NUMERO_ENORME,
        "name_client_booking": "Cliente",
        "date_booking": "2099-01-01",
        "start_time_booking": "21:00",
        "qty_booking": 2,
    })
    assert response.status_code == 400

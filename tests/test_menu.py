from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_menus():
    response = client.get("/menus/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_menu_not_found():
    response = client.get("/menus/999999")
    assert response.status_code == 404

assert response.json() == {"detail": "Menú con id_menu 999999 no encontrado"}
 
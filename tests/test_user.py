import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def random_email() -> str:
    # Email aleatorio para que los tests no choquen con datos existentes
    return f"test_{uuid.uuid4().hex[:8]}@test.com"


def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_user_not_found():
    response = client.get("/users/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Usuario con id_user 999999 no encontrado"}


def test_create_user_restaurant_not_found():
    response = client.post("/users/", json={
        "name_user": "Usuario test",
        "email_user": random_email(),
        "pass_user": "1234",
        "role_user": "camarero",
        "id_rest_user": 999999,
    })
    assert response.status_code == 400


def test_create_user_invalid_data():
    user = {
        "name_user": "Usuario test",
        "email_user": random_email(),
        "pass_user": "1234",
        "role_user": "camarero",
        "id_rest_user": 1,
    }
    # Rol que no existe
    assert client.post("/users/", json={**user, "role_user": "cocinero"}).status_code == 422
    # Nombre vacío
    assert client.post("/users/", json={**user, "name_user": ""}).status_code == 422
    # Falta la contraseña
    user_without_pass = {k: v for k, v in user.items() if k != "pass_user"}
    assert client.post("/users/", json=user_without_pass).status_code == 422


def test_update_and_delete_user_not_found():
    assert client.put("/users/999999", json={"name_user": "X"}).status_code == 404
    assert client.delete("/users/999999").status_code == 404


def test_user_crud_flow():
    # Restaurante temporal solo para este test
    restaurant = client.post("/restaurants/", json={
        "cif_rest": f"T{uuid.uuid4().hex[:8].upper()}",
        "name_rest": "Restaurante test usuarios",
    }).json()
    id_rest = restaurant["id_rest"]
    email = random_email()

    try:
        # Crear
        response = client.post("/users/", json={
            "name_user": "Camarero test",
            "email_user": email,
            "pass_user": "1234",
            "role_user": "camarero",
            "id_rest_user": id_rest,
        })
        assert response.status_code == 201
        user = response.json()
        assert "pass_user" not in user  # la contraseña nunca se devuelve

        # Email repetido
        response = client.post("/users/", json={
            "name_user": "Otro",
            "email_user": email,
            "pass_user": "1234",
            "role_user": "camarero",
            "id_rest_user": id_rest,
        })
        assert response.status_code == 400

        # Consultar
        response = client.get(f"/users/{user['id_user']}")
        assert response.status_code == 200
        assert response.json()["email_user"] == email

        # Actualizar
        response = client.put(f"/users/{user['id_user']}", json={"role_user": "administrador"})
        assert response.status_code == 200
        assert response.json()["role_user"] == "administrador"

        # Actualizar con un restaurante que no existe
        response = client.put(f"/users/{user['id_user']}", json={"id_rest_user": 999999})
        assert response.status_code == 400

        # Borrar
        response = client.delete(f"/users/{user['id_user']}")
        assert response.status_code == 200
        assert client.get(f"/users/{user['id_user']}").status_code == 404
    finally:
        client.delete(f"/restaurants/{id_rest}")

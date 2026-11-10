from datetime import date, time
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.core.database_connection import SessionLocal
from app.models.restaurant_model import RestaurantModel
from app.models.user_model import UserModel
from app.models.shift_model import ShiftModel, ShiftAssignmentModel
from app.schemas.enums import UserRole, ShiftName

client = TestClient(app)


def test_get_shift_assignments_empty_or_list():
    response = client.get("/shift-assignments/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_shift_assignment_not_found():
    response = client.get("/shift-assignments/999999")
    assert response.status_code == 404


def test_create_shift_assignment_invalid_fks():
    payload = {
        "id_user_assign": 999999,
        "id_shift_assign": 999999,
        "date_assign": "2026-11-10",
        "actual_arrival_assign": "09:00:00",
        "actual_departure_assign": "17:00:00",
    }
    response = client.post("/shift-assignments/", json=payload)
    assert response.status_code == 400
    assert "no existe" in response.json()["detail"]


def test_full_shift_assignment_crud_lifecycle():
    db = SessionLocal()
    # 1. Setup prerequisite records: restaurant, user, shift
    restaurant = RestaurantModel(
        cif_rest="B11223344",
        name_rest="Restaurante Test Shift",
        address_rest="Calle Prueba 123",
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    user = UserModel(
        id_rest_user=restaurant.id_rest,
        name_user="Camarero Test",
        email_user="camarero_test@test.com",
        pass_user="hashed_pass",
        role_user=UserRole.camarero,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    shift = ShiftModel(
        id_rest_shift=restaurant.id_rest,
        name_shift=ShiftName.manana,
        open_time_shift=time(8, 0, 0),
        close_time_shift=time(16, 0, 0),
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)

    try:
        # 2. CREATE (POST)
        payload = {
            "id_user_assign": user.id_user,
            "id_shift_assign": shift.id_shift,
            "date_assign": "2026-11-10",
            "actual_arrival_assign": "08:05:00",
            "actual_departure_assign": "16:02:00",
        }
        create_res = client.post("/shift-assignments/", json=payload)
        assert create_res.status_code == 201
        created_data = create_res.json()
        id_assign = created_data["id_assign"]
        assert created_data["id_user_assign"] == user.id_user
        assert created_data["id_shift_assign"] == shift.id_shift
        assert created_data["date_assign"] == "2026-11-10"

        # 3. READ (GET by ID)
        get_res = client.get(f"/shift-assignments/{id_assign}")
        assert get_res.status_code == 200
        assert get_res.json()["id_assign"] == id_assign

        # 4. LIST (GET with filters)
        list_res = client.get(
            f"/shift-assignments/?id_user={user.id_user}&id_shift={shift.id_shift}&date_assign=2026-11-10"
        )
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1
        assert any(item["id_assign"] == id_assign for item in list_res.json())

        # 5. UPDATE (PUT)
        update_payload = {
            "actual_arrival_assign": "08:15:00",
            "actual_departure_assign": "16:30:00",
        }
        put_res = client.put(f"/shift-assignments/{id_assign}", json=update_payload)
        assert put_res.status_code == 200
        assert put_res.json()["actual_arrival_assign"] == "08:15:00"
        assert put_res.json()["actual_departure_assign"] == "16:30:00"

        # 6. DELETE (DELETE)
        del_res = client.delete(f"/shift-assignments/{id_assign}")
        assert del_res.status_code == 200

        # Verify deletion
        get_deleted_res = client.get(f"/shift-assignments/{id_assign}")
        assert get_deleted_res.status_code == 404

    finally:
        # 7. Teardown
        db.query(ShiftAssignmentModel).filter(
            ShiftAssignmentModel.id_user_assign == user.id_user
        ).delete()
        db.delete(shift)
        db.delete(user)
        db.delete(restaurant)
        db.commit()
        db.close()


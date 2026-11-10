from datetime import date, time
from fastapi.testclient import TestClient

from app.main import app
from app.core.database_connection import SessionLocal
from app.models.restaurant_model import RestaurantModel
from app.models.user_model import UserModel
from app.models.shift_model import ShiftModel, ShiftAssignmentModel, ShiftTableRelModel
from app.models.table_model import RestaurantTableModel
from app.schemas.enums import UserRole, ShiftName, TableLocation

client = TestClient(app)


def test_get_shift_table_rels_empty_or_list():
    response = client.get("/shift-table-rels/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_shift_table_rel_not_found():
    response = client.get("/shift-table-rels/999999")
    assert response.status_code == 404


def test_create_shift_table_rel_invalid_fks():
    payload = {
        "id_assign_shift_table_rel": 999999,
        "id_table_shift_table_rel": 999999,
    }
    response = client.post("/shift-table-rels/", json=payload)
    assert response.status_code == 400
    assert "no existe" in response.json()["detail"]


def test_full_shift_table_rel_crud_lifecycle():
    db = SessionLocal()

    # 1. Setup prerequisite records
    restaurant = RestaurantModel(
        cif_rest="B55667788",
        name_rest="Restaurante Test Shift Table",
        address_rest="Calle Rel 123",
    )
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    user = UserModel(
        id_rest_user=restaurant.id_rest,
        name_user="Camarero Rel",
        email_user="camarero_rel@test.com",
        pass_user="hashed_pass",
        role_user=UserRole.camarero,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    shift = ShiftModel(
        id_rest_shift=restaurant.id_rest,
        name_shift=ShiftName.tarde,
        open_time_shift=time(16, 0, 0),
        close_time_shift=time(23, 59, 0),
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)

    assignment = ShiftAssignmentModel(
        id_user_assign=user.id_user,
        id_shift_assign=shift.id_shift,
        date_assign=date(2026, 11, 10),
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    table1 = RestaurantTableModel(
        id_rest_table=restaurant.id_rest,
        name_table="Mesa 1",
        cap_table=4,
        location_table=TableLocation.interior,
    )
    table2 = RestaurantTableModel(
        id_rest_table=restaurant.id_rest,
        name_table="Mesa 2",
        cap_table=6,
        location_table=TableLocation.terraza,
    )
    db.add_all([table1, table2])
    db.commit()
    db.refresh(table1)
    db.refresh(table2)

    try:
        # 2. CREATE (POST)
        payload = {
            "id_assign_shift_table_rel": assignment.id_assign,
            "id_table_shift_table_rel": table1.id_table,
        }
        create_res = client.post("/shift-table-rels/", json=payload)
        assert create_res.status_code == 201
        created_data = create_res.json()
        id_rel = created_data["id_shift_table_rel"]
        assert created_data["id_assign_shift_table_rel"] == assignment.id_assign
        assert created_data["id_table_shift_table_rel"] == table1.id_table

        # 3. READ (GET by ID)
        get_res = client.get(f"/shift-table-rels/{id_rel}")
        assert get_res.status_code == 200
        assert get_res.json()["id_shift_table_rel"] == id_rel

        # 4. LIST (GET with filters)
        list_res = client.get(
            f"/shift-table-rels/?id_assign={assignment.id_assign}&id_table={table1.id_table}"
        )
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1
        assert any(item["id_shift_table_rel"] == id_rel for item in list_res.json())

        # 5. UPDATE (PUT)
        update_payload = {
            "id_table_shift_table_rel": table2.id_table,
        }
        put_res = client.put(f"/shift-table-rels/{id_rel}", json=update_payload)
        assert put_res.status_code == 200
        assert put_res.json()["id_table_shift_table_rel"] == table2.id_table

        # 6. DELETE (DELETE)
        del_res = client.delete(f"/shift-table-rels/{id_rel}")
        assert del_res.status_code == 200

        # Verify deletion
        get_deleted_res = client.get(f"/shift-table-rels/{id_rel}")
        assert get_deleted_res.status_code == 404

    finally:
        # 7. Teardown
        db.query(ShiftTableRelModel).filter(
            ShiftTableRelModel.id_assign_shift_table_rel == assignment.id_assign
        ).delete()
        db.delete(table1)
        db.delete(table2)
        db.delete(assignment)
        db.delete(shift)
        db.delete(user)
        db.delete(restaurant)
        db.commit()
        db.close()


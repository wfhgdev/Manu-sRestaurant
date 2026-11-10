from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.table_model import RestaurantTableModel, TableRelModel
from app.models.restaurant_model import RestaurantModel
from app.models.shift_model import ShiftTableRelModel
from app.schemas.table_schema import RestaurantTableCreate, RestaurantTableUpdate


def get_tables(db: Session, skip: int = 0, limit: int = 100, id_rest: int | None = None) -> list[RestaurantTableModel]:
    query = select(RestaurantTableModel)
    if id_rest is not None:
        query = query.where(RestaurantTableModel.id_rest_table == id_rest)
    query = query.order_by(RestaurantTableModel.id_table).offset(skip).limit(limit)
    return list(db.execute(query).scalars().all())


def get_table_by_id(db: Session, id_table: int) -> RestaurantTableModel | None:
    return db.execute(
        select(RestaurantTableModel).where(RestaurantTableModel.id_table == id_table)
    ).scalar_one_or_none()


def check_restaurant_exists(db: Session, id_rest: int) -> None:
    restaurant = db.execute(
        select(RestaurantModel).where(RestaurantModel.id_rest == id_rest)
    ).scalar_one_or_none()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante con id_rest {id_rest} no encontrado"
        )


def check_table_name_available(db: Session, id_rest: int, name_table: str, exclude_id: int | None = None) -> None:
    # Dentro de un mismo restaurante no puede haber dos mesas con el mismo nombre
    query = select(RestaurantTableModel).where(
        RestaurantTableModel.id_rest_table == id_rest,
        RestaurantTableModel.name_table == name_table,
    )
    if exclude_id is not None:
        query = query.where(RestaurantTableModel.id_table != exclude_id)

    if db.execute(query).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una mesa llamada '{name_table}' en el restaurante {id_rest}"
        )


def create_table(db: Session, table: RestaurantTableCreate) -> RestaurantTableModel:
    check_restaurant_exists(db, table.id_rest_table)
    check_table_name_available(db, table.id_rest_table, table.name_table)

    db_table = RestaurantTableModel(
        id_rest_table=table.id_rest_table,
        name_table=table.name_table,
        cap_table=table.cap_table,
        location_table=table.location_table,
        state_table=table.state_table,
    )
    try:
        db.add(db_table)
        db.commit()
        db.refresh(db_table)
        return db_table
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def update_table(db: Session, id_table: int, table_update: RestaurantTableUpdate) -> RestaurantTableModel:
    db_table = get_table_by_id(db, id_table)
    if not db_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mesa con id_table {id_table} no encontrada"
        )

    update_data = table_update.model_dump(exclude_unset=True)

    new_id_rest = update_data.get("id_rest_table", db_table.id_rest_table)
    new_name = update_data.get("name_table", db_table.name_table)

    if new_id_rest != db_table.id_rest_table:
        check_restaurant_exists(db, new_id_rest)
    if new_id_rest != db_table.id_rest_table or new_name != db_table.name_table:
        check_table_name_available(db, new_id_rest, new_name, exclude_id=id_table)

    for field, value in update_data.items():
        setattr(db_table, field, value)

    try:
        db.commit()
        db.refresh(db_table)
        return db_table
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def delete_table(db: Session, id_table: int) -> dict[str, str]:
    db_table = get_table_by_id(db, id_table)
    if not db_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mesa con id_table {id_table} no encontrada"
        )

    # Si la mesa ya se ha usado en reservas o turnos, no se borra (se perdería el historial).
    has_bookings = db.execute(
        select(TableRelModel).where(TableRelModel.id_table_table_rel == id_table)
    ).first()
    has_shifts = db.execute(
        select(ShiftTableRelModel).where(ShiftTableRelModel.id_table_shift_table_rel == id_table)
    ).first()
    if has_bookings or has_shifts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la mesa porque tiene reservas o turnos asociados. "
                   "Si ya no se usa, desactívala con state_table = false."
        )

    try:
        db.delete(db_table)
        db.commit()
        return {"message": f"Mesa con id_table {id_table} eliminada exitosamente"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la mesa porque tiene registros asociados."
        )

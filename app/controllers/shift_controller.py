from datetime import time
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.shift_model import ShiftModel, ShiftAssignmentModel
from app.models.restaurant_model import RestaurantModel
from app.schemas.enums import ShiftName
from app.schemas.shift_schema import ShiftCreate, ShiftUpdate


def get_shifts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_rest: int | None = None,
    name_shift: ShiftName | None = None,
) -> list[ShiftModel]:
    query = select(ShiftModel)
    if id_rest is not None:
        query = query.where(ShiftModel.id_rest_shift == id_rest)
    if name_shift is not None:
        query = query.where(ShiftModel.name_shift == name_shift)
    query = query.order_by(ShiftModel.id_shift).offset(skip).limit(limit)
    return list(db.execute(query).scalars().all())


def get_shift_by_id(db: Session, id_shift: int) -> ShiftModel | None:
    return db.execute(
        select(ShiftModel).where(ShiftModel.id_shift == id_shift)
    ).scalar_one_or_none()


def check_restaurant_exists(db: Session, id_rest: int) -> None:
    restaurant = db.execute(
        select(RestaurantModel).where(RestaurantModel.id_rest == id_rest)
    ).scalar_one_or_none()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante con id_rest {id_rest} no encontrado",
        )


def check_shift_name_available(
    db: Session, id_rest: int, name_shift: ShiftName, exclude_id: int | None = None
) -> None:
    query = select(ShiftModel).where(
        ShiftModel.id_rest_shift == id_rest,
        ShiftModel.name_shift == name_shift,
    )
    if exclude_id is not None:
        query = query.where(ShiftModel.id_shift != exclude_id)

    if db.execute(query).first():
        val = name_shift.value if isinstance(name_shift, ShiftName) else str(name_shift)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un turno '{val}' en el restaurante {id_rest}",
        )


def check_shift_times(open_time: time, close_time: time) -> None:
    if open_time == close_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La hora de apertura y de cierre no pueden ser idénticas.",
        )


def create_shift(db: Session, shift: ShiftCreate) -> ShiftModel:
    check_restaurant_exists(db, shift.id_rest_shift)
    check_shift_times(shift.open_time_shift, shift.close_time_shift)
    check_shift_name_available(db, shift.id_rest_shift, shift.name_shift)

    db_shift = ShiftModel(
        id_rest_shift=shift.id_rest_shift,
        name_shift=shift.name_shift,
        open_time_shift=shift.open_time_shift,
        close_time_shift=shift.close_time_shift,
    )
    try:
        db.add(db_shift)
        db.commit()
        db.refresh(db_shift)
        return db_shift
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}",
        )


def update_shift(db: Session, id_shift: int, shift_update: ShiftUpdate) -> ShiftModel:
    db_shift = get_shift_by_id(db, id_shift)
    if not db_shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Turno con id_shift {id_shift} no encontrado",
        )

    update_data = shift_update.model_dump(exclude_unset=True)

    new_id_rest = update_data.get("id_rest_shift", db_shift.id_rest_shift)
    new_name = update_data.get("name_shift", db_shift.name_shift)
    new_open_time = update_data.get("open_time_shift", db_shift.open_time_shift)
    new_close_time = update_data.get("close_time_shift", db_shift.close_time_shift)

    if new_id_rest != db_shift.id_rest_shift:
        check_restaurant_exists(db, new_id_rest)

    check_shift_times(new_open_time, new_close_time)

    if new_id_rest != db_shift.id_rest_shift or new_name != db_shift.name_shift:
        check_shift_name_available(db, new_id_rest, new_name, exclude_id=id_shift)

    for field, value in update_data.items():
        setattr(db_shift, field, value)

    try:
        db.commit()
        db.refresh(db_shift)
        return db_shift
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}",
        )


def delete_shift(db: Session, id_shift: int) -> dict[str, str]:
    db_shift = get_shift_by_id(db, id_shift)
    if not db_shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Turno con id_shift {id_shift} no encontrado",
        )

    has_assignments = db.execute(
        select(ShiftAssignmentModel).where(ShiftAssignmentModel.id_shift_assign == id_shift)
    ).first()
    if has_assignments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el turno con id_shift {id_shift} porque tiene asignaciones de turno asociadas.",
        )

    try:
        db.delete(db_shift)
        db.commit()
        return {"message": f"Turno con id_shift {id_shift} eliminado exitosamente"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el turno porque tiene registros asociados.",
        )


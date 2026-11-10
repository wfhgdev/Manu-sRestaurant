from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.shift_model import ShiftAssignmentModel, ShiftModel
from app.models.user_model import UserModel
from app.schemas.shift_assignment_schema import ShiftAssignmentCreate, ShiftAssignmentUpdate


def get_shift_assignments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_user: int | None = None,
    id_shift: int | None = None,
    date_assign: date | None = None,
) -> list[ShiftAssignmentModel]:
    query = select(ShiftAssignmentModel)
    if id_user is not None:
        query = query.where(ShiftAssignmentModel.id_user_assign == id_user)
    if id_shift is not None:
        query = query.where(ShiftAssignmentModel.id_shift_assign == id_shift)
    if date_assign is not None:
        query = query.where(ShiftAssignmentModel.date_assign == date_assign)
    return list(db.execute(query.offset(skip).limit(limit)).scalars().all())


def get_shift_assignment_by_id(db: Session, id_assign: int) -> ShiftAssignmentModel | None:
    return db.execute(
        select(ShiftAssignmentModel).where(ShiftAssignmentModel.id_assign == id_assign)
    ).scalar_one_or_none()


def check_user_exists(db: Session, id_user: int) -> bool:
    return db.execute(select(UserModel).where(UserModel.id_user == id_user)).scalar_one_or_none() is not None


def check_shift_exists(db: Session, id_shift: int) -> bool:
    return db.execute(select(ShiftModel).where(ShiftModel.id_shift == id_shift)).scalar_one_or_none() is not None


def check_assignment_not_duplicated(
    db: Session, id_user: int, id_shift: int, date_assign: date, exclude_id: int | None = None
) -> None:
    # Un mismo usuario no puede tener dos veces el mismo turno el mismo día
    query = select(ShiftAssignmentModel).where(
        ShiftAssignmentModel.id_user_assign == id_user,
        ShiftAssignmentModel.id_shift_assign == id_shift,
        ShiftAssignmentModel.date_assign == date_assign,
    )
    if exclude_id is not None:
        query = query.where(ShiftAssignmentModel.id_assign != exclude_id)
    if db.execute(query).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ese usuario ya tiene asignado ese turno en esa fecha.",
        )


def create_shift_assignment(db: Session, assignment: ShiftAssignmentCreate) -> ShiftAssignmentModel:
    if not check_user_exists(db, assignment.id_user_assign):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El usuario con id_user '{assignment.id_user_assign}' no existe.",
        )

    if not check_shift_exists(db, assignment.id_shift_assign):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El turno con id_shift '{assignment.id_shift_assign}' no existe.",
        )

    check_assignment_not_duplicated(
        db, assignment.id_user_assign, assignment.id_shift_assign, assignment.date_assign
    )

    db_assignment = ShiftAssignmentModel(
        id_user_assign=assignment.id_user_assign,
        id_shift_assign=assignment.id_shift_assign,
        date_assign=assignment.date_assign,
        actual_arrival_assign=assignment.actual_arrival_assign,
        actual_departure_assign=assignment.actual_departure_assign,
    )
    try:
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}",
        )


def update_shift_assignment(
    db: Session, id_assign: int, assignment_update: ShiftAssignmentUpdate
) -> ShiftAssignmentModel:
    db_assignment = get_shift_assignment_by_id(db, id_assign)
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asignación de turno con id_assign {id_assign} no encontrada.",
        )

    update_data = assignment_update.model_dump(exclude_unset=True)

    if "id_user_assign" in update_data and update_data["id_user_assign"] is not None:
        if not check_user_exists(db, update_data["id_user_assign"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El usuario con id_user '{update_data['id_user_assign']}' no existe.",
            )

    if "id_shift_assign" in update_data and update_data["id_shift_assign"] is not None:
        if not check_shift_exists(db, update_data["id_shift_assign"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El turno con id_shift '{update_data['id_shift_assign']}' no existe.",
            )

    check_assignment_not_duplicated(
        db,
        update_data.get("id_user_assign") or db_assignment.id_user_assign,
        update_data.get("id_shift_assign") or db_assignment.id_shift_assign,
        update_data.get("date_assign") or db_assignment.date_assign,
        exclude_id=id_assign,
    )

    for field, value in update_data.items():
        setattr(db_assignment, field, value)

    try:
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}",
        )


def delete_shift_assignment(db: Session, id_assign: int) -> dict[str, str]:
    db_assignment = get_shift_assignment_by_id(db, id_assign)
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asignación de turno con id_assign {id_assign} no encontrada.",
        )

    try:
        db.delete(db_assignment)
        db.commit()
        return {"message": f"Asignación de turno con id_assign {id_assign} eliminada exitosamente."}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la asignación de turno porque tiene registros asociados (como mesas asignadas).",
        )


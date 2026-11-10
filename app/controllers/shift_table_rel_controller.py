from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.shift_model import ShiftTableRelModel, ShiftAssignmentModel
from app.models.table_model import RestaurantTableModel
from app.schemas.shift_table_rel_schema import ShiftTableRelCreate, ShiftTableRelUpdate


def get_shift_table_rels(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    id_assign: int | None = None,
    id_table: int | None = None,
) -> list[ShiftTableRelModel]:
    query = select(ShiftTableRelModel)
    if id_assign is not None:
        query = query.where(ShiftTableRelModel.id_assign_shift_table_rel == id_assign)
    if id_table is not None:
        query = query.where(ShiftTableRelModel.id_table_shift_table_rel == id_table)
    return list(db.execute(query.offset(skip).limit(limit)).scalars().all())


def get_shift_table_rel_by_id(db: Session, id_shift_table_rel: int) -> ShiftTableRelModel | None:
    return db.execute(
        select(ShiftTableRelModel).where(
            ShiftTableRelModel.id_shift_table_rel == id_shift_table_rel
        )
    ).scalar_one_or_none()


def check_assignment_exists(db: Session, id_assign: int) -> bool:
    return db.execute(
        select(ShiftAssignmentModel).where(ShiftAssignmentModel.id_assign == id_assign)
    ).scalar_one_or_none() is not None


def check_table_exists(db: Session, id_table: int) -> bool:
    return db.execute(
        select(RestaurantTableModel).where(RestaurantTableModel.id_table == id_table)
    ).scalar_one_or_none() is not None


def check_rel_not_duplicated(
    db: Session, id_assign: int, id_table: int, exclude_id: int | None = None
) -> None:
    # La misma mesa no puede estar dos veces en la misma asignación de turno
    query = select(ShiftTableRelModel).where(
        ShiftTableRelModel.id_assign_shift_table_rel == id_assign,
        ShiftTableRelModel.id_table_shift_table_rel == id_table,
    )
    if exclude_id is not None:
        query = query.where(ShiftTableRelModel.id_shift_table_rel != exclude_id)
    if db.execute(query).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esa mesa ya está asignada a esa asignación de turno.",
        )


def create_shift_table_rel(db: Session, rel: ShiftTableRelCreate) -> ShiftTableRelModel:
    if not check_assignment_exists(db, rel.id_assign_shift_table_rel):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La asignación de turno con id_assign '{rel.id_assign_shift_table_rel}' no existe.",
        )

    if not check_table_exists(db, rel.id_table_shift_table_rel):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La mesa con id_table '{rel.id_table_shift_table_rel}' no existe.",
        )

    check_rel_not_duplicated(db, rel.id_assign_shift_table_rel, rel.id_table_shift_table_rel)

    db_rel = ShiftTableRelModel(
        id_assign_shift_table_rel=rel.id_assign_shift_table_rel,
        id_table_shift_table_rel=rel.id_table_shift_table_rel,
    )
    try:
        db.add(db_rel)
        db.commit()
        db.refresh(db_rel)
        return db_rel
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}",
        )


def update_shift_table_rel(
    db: Session, id_shift_table_rel: int, rel_update: ShiftTableRelUpdate
) -> ShiftTableRelModel:
    db_rel = get_shift_table_rel_by_id(db, id_shift_table_rel)
    if not db_rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relación turno-mesa con id_shift_table_rel {id_shift_table_rel} no encontrada.",
        )

    update_data = rel_update.model_dump(exclude_unset=True)

    if (
        "id_assign_shift_table_rel" in update_data
        and update_data["id_assign_shift_table_rel"] is not None
    ):
        if not check_assignment_exists(db, update_data["id_assign_shift_table_rel"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La asignación de turno con id_assign '{update_data['id_assign_shift_table_rel']}' no existe.",
            )

    if (
        "id_table_shift_table_rel" in update_data
        and update_data["id_table_shift_table_rel"] is not None
    ):
        if not check_table_exists(db, update_data["id_table_shift_table_rel"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La mesa con id_table '{update_data['id_table_shift_table_rel']}' no existe.",
            )

    check_rel_not_duplicated(
        db,
        update_data.get("id_assign_shift_table_rel") or db_rel.id_assign_shift_table_rel,
        update_data.get("id_table_shift_table_rel") or db_rel.id_table_shift_table_rel,
        exclude_id=id_shift_table_rel,
    )

    for field, value in update_data.items():
        setattr(db_rel, field, value)

    try:
        db.commit()
        db.refresh(db_rel)
        return db_rel
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}",
        )


def delete_shift_table_rel(db: Session, id_shift_table_rel: int) -> dict[str, str]:
    db_rel = get_shift_table_rel_by_id(db, id_shift_table_rel)
    if not db_rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relación turno-mesa con id_shift_table_rel {id_shift_table_rel} no encontrada.",
        )

    try:
        db.delete(db_rel)
        db.commit()
        return {
            "message": f"Relación turno-mesa con id_shift_table_rel {id_shift_table_rel} eliminada exitosamente."
        }
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la relación turno-mesa debido a restricciones de integridad en base de datos.",
        )


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.shift_table_rel_schema import (
    ShiftTableRelCreate,
    ShiftTableRelUpdate,
    ShiftTableRelResponse,
)
from app.controllers import shift_table_rel_controller

router = APIRouter(prefix="/shift-table-rels", tags=["Shift Table Relations"])


@router.post("/", response_model=ShiftTableRelResponse, status_code=status.HTTP_201_CREATED)
def create_new_shift_table_rel(rel: ShiftTableRelCreate, db: Session = Depends(get_db)):
    return shift_table_rel_controller.create_shift_table_rel(db=db, rel=rel)


@router.get("/", response_model=list[ShiftTableRelResponse])
def get_all_shift_table_rels(
    skip: int = 0,
    limit: int = 100,
    id_assign: int | None = None,
    id_table: int | None = None,
    db: Session = Depends(get_db),
):
    return shift_table_rel_controller.get_shift_table_rels(
        db=db, skip=skip, limit=limit, id_assign=id_assign, id_table=id_table
    )


@router.get("/{id_shift_table_rel}", response_model=ShiftTableRelResponse)
def get_shift_table_rel(id_shift_table_rel: int, db: Session = Depends(get_db)):
    rel = shift_table_rel_controller.get_shift_table_rel_by_id(
        db=db, id_shift_table_rel=id_shift_table_rel
    )
    if not rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relación turno-mesa con id_shift_table_rel {id_shift_table_rel} no encontrada.",
        )
    return rel


@router.put("/{id_shift_table_rel}", response_model=ShiftTableRelResponse)
def update_shift_table_rel_by_id(
    id_shift_table_rel: int,
    rel_update: ShiftTableRelUpdate,
    db: Session = Depends(get_db),
):
    return shift_table_rel_controller.update_shift_table_rel(
        db=db, id_shift_table_rel=id_shift_table_rel, rel_update=rel_update
    )


@router.delete("/{id_shift_table_rel}", status_code=status.HTTP_200_OK)
def delete_shift_table_rel_by_id(id_shift_table_rel: int, db: Session = Depends(get_db)):
    return shift_table_rel_controller.delete_shift_table_rel(
        db=db, id_shift_table_rel=id_shift_table_rel
    )


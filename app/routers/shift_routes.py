from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.enums import ShiftName
from app.schemas.shift_schema import ShiftCreate, ShiftUpdate, ShiftResponse
from app.controllers import shift_controller

router = APIRouter(prefix="/shifts", tags=["Shifts"])


@router.post("/", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
def create_new_shift(shift: ShiftCreate, db: Session = Depends(get_db)):
    return shift_controller.create_shift(db=db, shift=shift)


@router.get("/", response_model=list[ShiftResponse])
def get_all_shifts(
    skip: int = 0,
    limit: int = 100,
    id_rest: int | None = None,
    name_shift: ShiftName | None = None,
    db: Session = Depends(get_db),
):
    return shift_controller.get_shifts(
        db=db, skip=skip, limit=limit, id_rest=id_rest, name_shift=name_shift
    )


@router.get("/{id_shift}", response_model=ShiftResponse)
def get_shift(id_shift: int, db: Session = Depends(get_db)):
    shift = shift_controller.get_shift_by_id(db=db, id_shift=id_shift)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Turno con id_shift {id_shift} no encontrado",
        )
    return shift


@router.put("/{id_shift}", response_model=ShiftResponse)
def update_shift_by_id(
    id_shift: int, shift_update: ShiftUpdate, db: Session = Depends(get_db)
):
    return shift_controller.update_shift(
        db=db, id_shift=id_shift, shift_update=shift_update
    )


@router.delete("/{id_shift}", status_code=status.HTTP_200_OK)
def delete_shift_by_id(id_shift: int, db: Session = Depends(get_db)):
    return shift_controller.delete_shift(db=db, id_shift=id_shift)


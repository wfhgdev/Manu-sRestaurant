from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.shift_assignment_schema import (
    ShiftAssignmentCreate,
    ShiftAssignmentUpdate,
    ShiftAssignmentResponse,
)
from app.controllers import shift_assignment_controller

router = APIRouter(prefix="/shift-assignments", tags=["Shift Assignments"])


@router.post("/", response_model=ShiftAssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_new_shift_assignment(assignment: ShiftAssignmentCreate, db: Session = Depends(get_db)):
    return shift_assignment_controller.create_shift_assignment(db=db, assignment=assignment)


@router.get("/", response_model=list[ShiftAssignmentResponse])
def get_all_shift_assignments(
    skip: int = 0,
    limit: int = 100,
    id_user: int | None = None,
    id_shift: int | None = None,
    date_assign: date | None = None,
    db: Session = Depends(get_db),
):
    return shift_assignment_controller.get_shift_assignments(
        db=db, skip=skip, limit=limit, id_user=id_user, id_shift=id_shift, date_assign=date_assign
    )


@router.get("/{id_assign}", response_model=ShiftAssignmentResponse)
def get_shift_assignment(id_assign: int, db: Session = Depends(get_db)):
    assignment = shift_assignment_controller.get_shift_assignment_by_id(db=db, id_assign=id_assign)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asignación de turno con id_assign {id_assign} no encontrada.",
        )
    return assignment


@router.put("/{id_assign}", response_model=ShiftAssignmentResponse)
def update_shift_assignment_by_id(
    id_assign: int, assignment_update: ShiftAssignmentUpdate, db: Session = Depends(get_db)
):
    return shift_assignment_controller.update_shift_assignment(
        db=db, id_assign=id_assign, assignment_update=assignment_update
    )


@router.delete("/{id_assign}", status_code=status.HTTP_200_OK)
def delete_shift_assignment_by_id(id_assign: int, db: Session = Depends(get_db)):
    return shift_assignment_controller.delete_shift_assignment(db=db, id_assign=id_assign)


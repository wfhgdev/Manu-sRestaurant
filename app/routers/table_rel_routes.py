from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.table_rel_schema import TableRelCreate, TableRelUpdate, TableRelResponse
from app.controllers import table_rel_controller

router = APIRouter(prefix="/table-rels", tags=["Table Relations"])


@router.post("/", response_model=TableRelResponse, status_code=status.HTTP_201_CREATED)
def create_new_table_rel(rel: TableRelCreate, db: Session = Depends(get_db)):
    return table_rel_controller.create_table_rel(db=db, rel=rel)


@router.get("/", response_model=list[TableRelResponse])
def get_all_table_rels(
    skip: int = 0,
    limit: int = 100,
    id_booking: int | None = None,
    id_table: int | None = None,
    db: Session = Depends(get_db),
):
    # Filtros opcionales: /table-rels/?id_booking=1 (mesas de una reserva) o ?id_table=3 (reservas de una mesa)
    return table_rel_controller.get_table_rels(
        db=db, skip=skip, limit=limit, id_booking=id_booking, id_table=id_table
    )


# table_rel no tiene id propio: cada relación se identifica por la pareja (reserva, mesa)
@router.get("/{id_booking}/{id_table}", response_model=TableRelResponse)
def get_table_rel(id_booking: int, id_table: int, db: Session = Depends(get_db)):
    rel = table_rel_controller.get_table_rel(db=db, id_booking=id_booking, id_table=id_table)
    if not rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La mesa {id_table} no está asignada a la reserva {id_booking}"
        )
    return rel


@router.put("/{id_booking}/{id_table}", response_model=TableRelResponse)
def update_table_rel_by_ids(
    id_booking: int,
    id_table: int,
    rel_update: TableRelUpdate,
    db: Session = Depends(get_db),
):
    return table_rel_controller.update_table_rel(
        db=db, id_booking=id_booking, id_table=id_table, rel_update=rel_update
    )


@router.delete("/{id_booking}/{id_table}", status_code=status.HTTP_200_OK)
def delete_table_rel_by_ids(id_booking: int, id_table: int, db: Session = Depends(get_db)):
    return table_rel_controller.delete_table_rel(db=db, id_booking=id_booking, id_table=id_table)

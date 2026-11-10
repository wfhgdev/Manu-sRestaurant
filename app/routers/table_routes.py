from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.table_schema import RestaurantTableCreate, RestaurantTableUpdate, RestaurantTableResponse
from app.controllers import table_controller

router = APIRouter(prefix="/tables", tags=["Tables"])


@router.post("/", response_model=RestaurantTableResponse, status_code=status.HTTP_201_CREATED)
def create_new_table(table: RestaurantTableCreate, db: Session = Depends(get_db)):
    return table_controller.create_table(db=db, table=table)


@router.get("/", response_model=list[RestaurantTableResponse])
def get_all_tables(skip: int = 0, limit: int = 100, id_rest: int | None = None, db: Session = Depends(get_db)):
    # id_rest es opcional: /tables/?id_rest=1 devuelve solo las mesas de ese restaurante
    return table_controller.get_tables(db=db, skip=skip, limit=limit, id_rest=id_rest)


@router.get("/{id_table}", response_model=RestaurantTableResponse)
def get_table(id_table: int, db: Session = Depends(get_db)):
    table = table_controller.get_table_by_id(db=db, id_table=id_table)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mesa con id_table {id_table} no encontrada"
        )
    return table


@router.put("/{id_table}", response_model=RestaurantTableResponse)
def update_table_by_id(id_table: int, table_update: RestaurantTableUpdate, db: Session = Depends(get_db)):
    return table_controller.update_table(db=db, id_table=id_table, table_update=table_update)


@router.delete("/{id_table}", status_code=status.HTTP_200_OK)
def delete_table_by_id(id_table: int, db: Session = Depends(get_db)):
    return table_controller.delete_table(db=db, id_table=id_table)

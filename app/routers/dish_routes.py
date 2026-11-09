from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database_connection import get_db
from app.schemas.dish_schema import (
    DishCreate,
    DishUpdate,
    DishResponse,
)
from app.controllers import dish_controller


router = APIRouter(prefix="/dishes", tags=["Dishes"])


@router.post("/", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
def create_new_dish(dish: DishCreate, db: Session = Depends(get_db)):
    return dish_controller.create_dish(db=db, dish=dish)


@router.get("/", response_model=list[DishResponse])
def get_all_dishes(db: Session = Depends(get_db)):
    return dish_controller.get_dishes(db=db)


@router.get("/{id_dish}", response_model=DishResponse)
def get_dish(id_dish: int, db: Session = Depends(get_db)):
    dish = dish_controller.get_dish_by_id(db=db, id_dish=id_dish)

    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plato con id {id_dish} no encontrado"
        )

    return dish


@router.put("/{id_dish}", response_model=DishResponse)
def update_dish_by_id(
    id_dish: int,
    dish_update: DishUpdate,
    db: Session = Depends(get_db)
):
    return dish_controller.update_dish(
        db=db,
        id_dish=id_dish,
        dish_update=dish_update
    )


@router.delete("/{id_dish}", status_code=status.HTTP_200_OK)
def delete_dish_by_id(id_dish: int, db: Session = Depends(get_db)):
    return dish_controller.delete_dish(db=db, id_dish=id_dish)

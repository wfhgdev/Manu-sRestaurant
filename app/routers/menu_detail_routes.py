from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.menu_detail_schema import MenuDetailCreate, MenuDetailResponse
from app.controllers import menu_detail_controller

router = APIRouter(prefix="/menu-details", tags=["Menu details"])


@router.post("/", response_model=MenuDetailResponse, status_code=status.HTTP_201_CREATED)
def add_dish_to_menu(detail: MenuDetailCreate, db: Session = Depends(get_db)):
    return menu_detail_controller.add_dish_to_menu(db=db, detail=detail)


@router.get("/", response_model=list[MenuDetailResponse])
def get_all_menu_details(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return menu_detail_controller.get_menu_details(db=db, skip=skip, limit=limit)


@router.get("/menu/{id_menu}", response_model=list[MenuDetailResponse])
def get_dishes_of_menu(id_menu: int, db: Session = Depends(get_db)):
    return menu_detail_controller.get_dishes_of_menu(db=db, id_menu=id_menu)


@router.delete("/{id_menu}/{id_dish}", status_code=status.HTTP_200_OK)
def remove_dish_from_menu(id_menu: int, id_dish: int, db: Session = Depends(get_db)):
    return menu_detail_controller.remove_dish_from_menu(db=db, id_menu=id_menu, id_dish=id_dish)
    
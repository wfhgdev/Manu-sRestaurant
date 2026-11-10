from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.menu_schema import MenuCreate, MenuUpdate, MenuResponse
from app.controllers import menu_controller

router = APIRouter(prefix="/menus", tags=["Menus"])


@router.post("/", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
def create_new_menu(menu: MenuCreate, db: Session = Depends(get_db)):
    return menu_controller.create_menu(db=db, menu=menu)


@router.get("/", response_model=list[MenuResponse])
def get_all_menus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return menu_controller.get_menus(db=db, skip=skip, limit=limit)


@router.get("/{id_menu}", response_model=MenuResponse)
def get_menu(id_menu: int, db: Session = Depends(get_db)):
    menu = menu_controller.get_menu_by_id(db=db, id_menu=id_menu)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menú con id_menu {id_menu} no encontrado"
        )
    return menu


@router.put("/{id_menu}", response_model=MenuResponse)
def update_menu_by_id(id_menu: int, menu_update: MenuUpdate, db: Session = Depends(get_db)):
    return menu_controller.update_menu(db=db, id_menu=id_menu, menu_update=menu_update)


@router.delete("/{id_menu}", status_code=status.HTTP_200_OK)
def delete_menu_by_id(id_menu: int, db: Session = Depends(get_db)):
    return menu_controller.delete_menu(db=db, id_menu=id_menu)

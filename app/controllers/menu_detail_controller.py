from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.menu_model import MenuModel, MenuDetailModel
from app.models.dish_model import DishModel
from app.schemas.menu_detail_schema import MenuDetailCreate


def get_menu_details(db: Session, skip: int = 0, limit: int = 100) -> list[MenuDetailModel]:
    return list(db.execute(select(MenuDetailModel).offset(skip).limit(limit)).scalars().all())


def get_menu_detail(db: Session, id_menu: int, id_dish: int) -> MenuDetailModel | None:
    return db.execute(
        select(MenuDetailModel).where(
            MenuDetailModel.id_menu_det == id_menu,
            MenuDetailModel.id_dish_det == id_dish,
        )
    ).scalar_one_or_none()


def get_dishes_of_menu(db: Session, id_menu: int) -> list[MenuDetailModel]:
    menu = db.execute(select(MenuModel).where(MenuModel.id_menu == id_menu)).scalar_one_or_none()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menú con id_menu {id_menu} no encontrado"
        )
    return list(
        db.execute(select(MenuDetailModel).where(MenuDetailModel.id_menu_det == id_menu)).scalars().all()
    )


def add_dish_to_menu(db: Session, detail: MenuDetailCreate) -> MenuDetailModel:
    menu = db.execute(
        select(MenuModel).where(MenuModel.id_menu == detail.id_menu_det)
    ).scalar_one_or_none()
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menú con id_menu {detail.id_menu_det} no encontrado"
        )

    dish = db.execute(
        select(DishModel).where(DishModel.id_dish == detail.id_dish_det)
    ).scalar_one_or_none()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plato con id_dish {detail.id_dish_det} no encontrado"
        )

    if dish.id_rest_dish != menu.id_rest_menu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El plato y el menú pertenecen a restaurantes distintos"
        )

    if get_menu_detail(db, detail.id_menu_det, detail.id_dish_det):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ese plato ya está en el menú"
        )

    db_detail = MenuDetailModel(
        id_menu_det=detail.id_menu_det,
        id_dish_det=detail.id_dish_det,
    )
    try:
        db.add(db_detail)
        db.commit()
        db.refresh(db_detail)
        return db_detail
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def remove_dish_from_menu(db: Session, id_menu: int, id_dish: int) -> dict[str, str]:
    db_detail = get_menu_detail(db, id_menu, id_dish)
    if not db_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El plato {id_dish} no está en el menú {id_menu}"
        )

    try:
        db.delete(db_detail)
        db.commit()
        return {"message": f"Plato {id_dish} quitado del menú {id_menu} exitosamente"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede quitar el plato del menú."
        )
        
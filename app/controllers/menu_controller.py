from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.menu_model import MenuModel
from app.models.restaurant_model import RestaurantModel
from app.schemas.menu_schema import MenuCreate, MenuUpdate


def get_menus(db: Session, skip: int = 0, limit: int = 100) -> list[MenuModel]:
    return list(db.execute(select(MenuModel).offset(skip).limit(limit)).scalars().all())


def get_menu_by_id(db: Session, id_menu: int) -> MenuModel | None:
    return db.execute(select(MenuModel).where(MenuModel.id_menu == id_menu)).scalar_one_or_none()


def check_restaurant_exists(db: Session, id_rest: int) -> None:
    restaurant = db.execute(
        select(RestaurantModel).where(RestaurantModel.id_rest == id_rest)
    ).scalar_one_or_none()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante con id_rest {id_rest} no encontrado"
        )


def create_menu(db: Session, menu: MenuCreate) -> MenuModel:
    check_restaurant_exists(db, menu.id_rest_menu)

    db_menu = MenuModel(
        id_rest_menu=menu.id_rest_menu,
        name_menu=menu.name_menu,
        price_menu=menu.price_menu,
        state_menu=menu.state_menu,
    )
    try:
        db.add(db_menu)
        db.commit()
        db.refresh(db_menu)
        return db_menu
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def update_menu(db: Session, id_menu: int, menu_update: MenuUpdate) -> MenuModel:
    db_menu = get_menu_by_id(db, id_menu)
    if not db_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menú con id_menu {id_menu} no encontrado"
        )

    update_data = menu_update.model_dump(exclude_unset=True)

    if "id_rest_menu" in update_data and update_data["id_rest_menu"] != db_menu.id_rest_menu:
        check_restaurant_exists(db, update_data["id_rest_menu"])

    for field, value in update_data.items():
        setattr(db_menu, field, value)

    try:
        db.commit()
        db.refresh(db_menu)
        return db_menu
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def delete_menu(db: Session, id_menu: int) -> dict[str, str]:
    db_menu = get_menu_by_id(db, id_menu)
    if not db_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menú con id_menu {id_menu} no encontrado"
        )

    try:
        db.delete(db_menu)
        db.commit()
        return {"message": f"Menú con id_menu {id_menu} eliminado exitosamente"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el menú porque tiene registros asociados."
        )
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.category_model import CategoryModel
from app.models.restaurant_model import RestaurantModel
from app.schemas.category_schema import CategoryCreate, CategoryUpdate


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[CategoryModel]:
    return list(db.execute(select(CategoryModel).offset(skip).limit(limit)).scalars().all())


def get_category_by_id(db: Session, id_cat_rest: int) -> CategoryModel | None:
    return db.execute(
        select(CategoryModel).where(CategoryModel.id_cat_rest == id_cat_rest)
    ).scalar_one_or_none()


def check_restaurant_exists(db: Session, id_rest: int) -> None:
    restaurant = db.execute(
        select(RestaurantModel).where(RestaurantModel.id_rest == id_rest)
    ).scalar_one_or_none()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante con id_rest {id_rest} no encontrado"
        )


def create_category(db: Session, category: CategoryCreate) -> CategoryModel:
    check_restaurant_exists(db, category.id_rest_cat_rest)

    db_category = CategoryModel(
        id_rest_cat_rest=category.id_rest_cat_rest,
        name_cat_rest=category.name_cat_rest,
        state_cat_rest=category.state_cat_rest,
    )
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def update_category(db: Session, id_cat_rest: int, category_update: CategoryUpdate) -> CategoryModel:
    db_category = get_category_by_id(db, id_cat_rest)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id_cat_rest {id_cat_rest} no encontrada"
        )

    update_data = category_update.model_dump(exclude_unset=True)

    if "id_rest_cat_rest" in update_data and update_data["id_rest_cat_rest"] != db_category.id_rest_cat_rest:
        check_restaurant_exists(db, update_data["id_rest_cat_rest"])

    for field, value in update_data.items():
        setattr(db_category, field, value)

    try:
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad en base de datos: {str(e.orig)}"
        )


def delete_category(db: Session, id_cat_rest: int) -> dict[str, str]:
    db_category = get_category_by_id(db, id_cat_rest)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id_cat_rest {id_cat_rest} no encontrada"
        )

    try:
        db.delete(db_category)
        db.commit()
        return {"message": f"Categoría con id_cat_rest {id_cat_rest} eliminada exitosamente"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar la categoría porque tiene registros asociados."
        )
        
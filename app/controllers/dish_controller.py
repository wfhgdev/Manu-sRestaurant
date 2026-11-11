from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.dish_model import DishModel, AllergenModel
from app.models.restaurant_model import RestaurantModel
from app.models.category_model import CategoryModel
from app.schemas.dish_schema import DishCreate, DishUpdate


def get_dishes(db: Session) -> list[DishModel]:
    query = select(DishModel).order_by(DishModel.id_dish)
    return list(db.execute(query).scalars().all())


def get_dish_by_id(db: Session, id_dish: int) -> DishModel | None:
    return db.execute(
        select(DishModel).where(DishModel.id_dish == id_dish)
    ).scalar_one_or_none()


def check_restaurant_and_category(db: Session, id_rest: int, id_cat: int) -> None:
    # El restaurante y la categoría deben existir, y la categoría debe ser de ese restaurante
    restaurant = db.execute(
        select(RestaurantModel).where(RestaurantModel.id_rest == id_rest)
    ).scalar_one_or_none()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurante con id_rest {id_rest} no encontrado"
        )

    category = db.execute(
        select(CategoryModel).where(CategoryModel.id_cat_rest == id_cat)
    ).scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id_cat_rest {id_cat} no encontrada"
        )

    if category.id_rest_cat_rest != id_rest:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La categoría no pertenece a ese restaurante"
        )


def create_dish(db: Session, dish: DishCreate) -> DishModel:
    check_restaurant_and_category(db, dish.id_rest_dish, dish.id_cat_dish)

    dish_data = dish.model_dump(exclude={"allergen_ids"})

    allergen_ids = dish.allergen_ids

    try:
        db_dish = DishModel(**dish_data)

        if allergen_ids:
            allergens = list(
                db.execute(
                    select(AllergenModel).where(
                        AllergenModel.id_allergen.in_(allergen_ids)
                    )
                ).scalars().all()
            )

            if len(allergens) != len(set(allergen_ids)):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Uno o varios alérgenos no existen."
                )

            db_dish.allergens = allergens

        db.add(db_dish)
        db.commit()
        db.refresh(db_dish)
        return db_dish

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se ha podido crear el plato."
        )


def update_dish(
    db: Session, id_dish: int, dish_update: DishUpdate
) -> DishModel:
    db_dish = get_dish_by_id(db, id_dish)

    if not db_dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plato con id {id_dish} no encontrado"
        )

    update_data = dish_update.model_dump(exclude_unset=True)
    allergen_ids = update_data.pop("allergen_ids", None)

    new_id_rest = update_data.get("id_rest_dish") or db_dish.id_rest_dish
    new_id_cat = update_data.get("id_cat_dish") or db_dish.id_cat_dish
    if new_id_rest != db_dish.id_rest_dish or new_id_cat != db_dish.id_cat_dish:
        check_restaurant_and_category(db, new_id_rest, new_id_cat)

    try:
        for field, value in update_data.items():
            setattr(db_dish, field, value)

        if allergen_ids is not None:
            allergens = list(
                db.execute(
                    select(AllergenModel).where(
                        AllergenModel.id_allergen.in_(allergen_ids)
                    )
                ).scalars().all()
            )

            if len(allergens) != len(set(allergen_ids)):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Uno o varios alérgenos no existen."
                )

            db_dish.allergens = allergens

        db.commit()
        db.refresh(db_dish)
        return db_dish

    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se ha podido actualizar el plato."
        )


def delete_dish(db: Session, id_dish: int) -> dict[str, str]:
    db_dish = get_dish_by_id(db, id_dish)

    if not db_dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plato con id {id_dish} no encontrado"
        )

    # Sin esta comprobación, el plato desaparecería de los menús sin avisar
    if db_dish.menus:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el plato porque está en uno o más menús. "
                   "Quítalo antes de los menús o desactívalo con state_dish = false."
        )

    try:
        db.delete(db_dish)
        db.commit()

        return {"message": f"Plato {id_dish} eliminado exitosamente"}

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el plato porque está asociado a otros registros."
        )

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.dish_model import DishModel, AllergenModel
from app.schemas.dish_schema import DishCreate, DishUpdate


def get_dishes(db: Session) -> list[DishModel]:
    query = select(DishModel).order_by(DishModel.id_dish)
    return list(db.execute(query).scalars().all())


def get_dish_by_id(db: Session, id_dish: int) -> DishModel | None:
    return db.execute(
        select(DishModel).where(DishModel.id_dish == id_dish)
    ).scalar_one_or_none()


def create_dish(db: Session, dish: DishCreate) -> DishModel:
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

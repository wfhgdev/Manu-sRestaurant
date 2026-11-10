from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.dish_model import AllergenModel
from app.schemas.allergen_schema import AllergenCreate, AllergenUpdate


def get_allergens(db: Session) -> list[AllergenModel]:
    query = select(AllergenModel).order_by(AllergenModel.id_allergen)
    return list(db.execute(query).scalars().all())


def get_allergen_by_id(db: Session, id_allergen: int) -> AllergenModel | None:
    return db.execute(
        select(AllergenModel).where(AllergenModel.id_allergen == id_allergen)
    ).scalar_one_or_none()


def create_allergen(db: Session, allergen: AllergenCreate) -> AllergenModel:
    db_allergen = AllergenModel(name_allergen=allergen.name_allergen)

    try:
        db.add(db_allergen)
        db.commit()
        db.refresh(db_allergen)
        return db_allergen
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se ha podido crear el alérgeno."
        )


def update_allergen(
    db: Session, id_allergen: int, allergen_update: AllergenUpdate
) -> AllergenModel:
    db_allergen = get_allergen_by_id(db, id_allergen)

    if not db_allergen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alérgeno con id {id_allergen} no encontrado"
        )

    update_data = allergen_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_allergen, field, value)

    db.commit()
    db.refresh(db_allergen)
    return db_allergen


def delete_allergen(db: Session, id_allergen: int) -> dict[str, str]:
    db_allergen = get_allergen_by_id(db, id_allergen)

    if not db_allergen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alérgeno con id {id_allergen} no encontrado"
        )

    if db_allergen.dishes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar el alérgeno porque está asociado a platos."
        )

    db.delete(db_allergen)
    db.commit()

    return {"message": f"Alérgeno {id_allergen} eliminado exitosamente"}
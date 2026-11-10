from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database_connection import get_db
from app.schemas.allergen_schema import (
    AllergenCreate,
    AllergenUpdate,
    AllergenResponse,
)
from app.controllers import allergen_controller


router = APIRouter(prefix="/allergens", tags=["Allergens"])


@router.post("/", response_model=AllergenResponse, status_code=status.HTTP_201_CREATED)
def create_new_allergen(allergen: AllergenCreate, db: Session = Depends(get_db)):
    return allergen_controller.create_allergen(db=db, allergen=allergen)


@router.get("/", response_model=list[AllergenResponse])
def get_all_allergens(db: Session = Depends(get_db)):
    return allergen_controller.get_allergens(db=db)


@router.get("/{id_allergen}", response_model=AllergenResponse)
def get_allergen(id_allergen: int, db: Session = Depends(get_db)):
    allergen = allergen_controller.get_allergen_by_id(db=db, id_allergen=id_allergen)

    if not allergen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alérgeno con id {id_allergen} no encontrado"
        )

    return allergen

@router.put("/{id_allergen}", response_model=AllergenResponse)
def update_allergen_by_id(
    id_allergen: int,
    allergen_update: AllergenUpdate,
    db: Session = Depends(get_db)
):
    return allergen_controller.update_allergen(
        db=db,
        id_allergen=id_allergen,
        allergen_update=allergen_update
    )

@router.delete("/{id_allergen}", status_code=status.HTTP_200_OK)
def delete_allergen_by_id(id_allergen: int, db: Session = Depends(get_db)):
    return allergen_controller.delete_allergen(db=db, id_allergen=id_allergen)
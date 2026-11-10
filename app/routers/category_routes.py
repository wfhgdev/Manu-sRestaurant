from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.category_schema import CategoryCreate, CategoryUpdate, CategoryResponse
from app.controllers import category_controller

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_new_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return category_controller.create_category(db=db, category=category)


@router.get("/", response_model=list[CategoryResponse])
def get_all_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return category_controller.get_categories(db=db, skip=skip, limit=limit)


@router.get("/{id_cat_rest}", response_model=CategoryResponse)
def get_category(id_cat_rest: int, db: Session = Depends(get_db)):
    category = category_controller.get_category_by_id(db=db, id_cat_rest=id_cat_rest)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id_cat_rest {id_cat_rest} no encontrada"
        )
    return category


@router.put("/{id_cat_rest}", response_model=CategoryResponse)
def update_category_by_id(id_cat_rest: int, category_update: CategoryUpdate, db: Session = Depends(get_db)):
    return category_controller.update_category(db=db, id_cat_rest=id_cat_rest, category_update=category_update)


@router.delete("/{id_cat_rest}", status_code=status.HTTP_200_OK)
def delete_category_by_id(id_cat_rest: int, db: Session = Depends(get_db)):
    return category_controller.delete_category(db=db, id_cat_rest=id_cat_rest)
    
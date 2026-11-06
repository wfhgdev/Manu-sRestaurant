from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database_connection import get_db
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.controllers import user_controller


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_controller.create_user(db=db, user=user)


@router.get("/", response_model=list[UserResponse])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_controller.get_users(db=db, skip=skip, limit=limit)


@router.get("/{id_user}", response_model=UserResponse)
def get_user(id_user: int, db: Session = Depends(get_db)):
    user = user_controller.get_user_by_id(db=db, id_user=id_user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id_user {id_user} no encontrado"
        )
    return user


@router.put("/{id_user}", response_model=UserResponse)
def update_user_by_id(id_user: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    return user_controller.update_user(db=db, id_user=id_user, user_update=user_update)


@router.delete("/{id_user}", status_code=status.HTTP_200_OK)
def delete_user_by_id(id_user: int, db: Session = Depends(get_db)):
    return user_controller.delete_user(db=db, id_user=id_user)

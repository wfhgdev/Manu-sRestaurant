from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user_model import UserModel
from app.schemas.user_schema import UserCreate, UserUpdate


def get_user_by_id(db: Session, id_user: int) -> UserModel | None:
    return db.execute(select(UserModel).where(UserModel.id_user == id_user)).scalar_one_or_none()


def get_user_by_email(db: Session, email_user: str) -> UserModel | None:
    return db.execute(select(UserModel).where(UserModel.email_user == email_user)).scalar_one_or_none()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[UserModel]:
    return list(db.execute(select(UserModel).offset(skip).limit(limit)).scalars().all())


def create_user(db: Session, user: UserCreate) -> UserModel:
    if get_user_by_email(db, user.email_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email '{user.email_user}' ya está registrado"
        )

    db_user = UserModel(
        name_user=user.name_user,
        email_user=user.email_user,
        pass_user=user.pass_user,
        id_rest_user=user.id_rest_user,
        tel_user=user.tel_user,
        role_user=user.role_user,
        state_user=user.state_user,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, id_user: int, user_update: UserUpdate) -> UserModel:
    db_user = get_user_by_id(db, id_user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id_user {id_user} no encontrado"
        )

    update_data = user_update.model_dump(exclude_unset=True)

    if "email_user" in update_data and update_data["email_user"] != db_user.email_user:
        if get_user_by_email(db, update_data["email_user"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El email '{update_data['email_user']}' ya está en uso"
            )

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, id_user: int) -> dict[str, str]:
    db_user = get_user_by_id(db, id_user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id_user {id_user} no encontrado"
        )

    db.delete(db_user)
    db.commit()
    return {"message": f"Usuario con id_user {id_user} eliminado exitosamente"}

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.controllers.user_controller import get_user_by_email
from app.core.security import verify_password
from app.models.user_model import UserModel
from app.schemas.auth_schema import LoginRequest


def authenticate_user(db: Session, login: LoginRequest) -> UserModel:
    user = get_user_by_email(db, login.email_user)

    if not user or not verify_password(login.pass_user, user.pass_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )

    return user

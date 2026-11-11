from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database_connection import get_db
from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.controllers import auth_controller


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = auth_controller.authenticate_user(db=db, login=login_data)
    return LoginResponse(
        message="Login correcto",
        id_user=user.id_user,
        name_user=user.name_user,
        role_user=user.role_user,
    )
from pydantic import BaseModel, Field
from app.schemas.enums import UserRole


class LoginRequest(BaseModel):
    email_user: str = Field(min_length=1, max_length=150)
    pass_user: str = Field(min_length=1, max_length=72)


class LoginResponse(BaseModel):
    message: str
    id_user: int
    name_user: str
    role_user: UserRole
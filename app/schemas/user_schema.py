from pydantic import BaseModel, ConfigDict
from app.schemas.enums import UserRole


class UserBase(BaseModel):
    name_user: str
    email_user: str
    id_rest_user: int
    tel_user: str | None = None
    role_user: UserRole


class UserCreate(UserBase):
    pass_user: str


class UserUpdate(BaseModel):
    name_user: str | None = None
    email_user: str | None = None
    pass_user: str | None = None
    id_rest_user: int | None = None
    tel_user: str | None = None
    role_user: UserRole | None = None


class UserResponse(UserBase):
    id_user: int

    model_config = ConfigDict(from_attributes=True)

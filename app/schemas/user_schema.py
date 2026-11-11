from pydantic import BaseModel, ConfigDict, Field
from app.schemas.enums import UserRole


class UserBase(BaseModel):
    name_user: str = Field(min_length=1, max_length=100)
    email_user: str = Field(min_length=1, max_length=150)
    id_rest_user: int
    tel_user: str | None = Field(default=None, max_length=20)
    role_user: UserRole


class UserCreate(UserBase):
    pass_user: str = Field(min_length=1, max_length=255)


class UserUpdate(BaseModel):
    name_user: str | None = Field(default=None, min_length=1, max_length=100)
    email_user: str | None = Field(default=None, min_length=1, max_length=150)
    pass_user: str | None = Field(default=None, min_length=1, max_length=255)
    id_rest_user: int | None = None
    tel_user: str | None = Field(default=None, max_length=20)
    role_user: UserRole | None = None


class UserResponse(UserBase):
    id_user: int

    model_config = ConfigDict(from_attributes=True)

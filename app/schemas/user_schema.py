import enum
from pydantic import BaseModel, ConfigDict


class UserRole(str, enum.Enum):
    administrador = "administrador"
    camarero = "camarero"
    superadministrador = "superadministrador"


class UserBase(BaseModel):
    name_user: str
    email_user: str
    id_rest_user: int | None = None
    tel_user: str | None = None
    role_user: UserRole
    state_user: bool = True


class UserCreate(UserBase):
    pass_user: str


class UserUpdate(BaseModel):
    name_user: str | None = None
    email_user: str | None = None
    pass_user: str | None = None
    id_rest_user: int | None = None
    tel_user: str | None = None
    role_user: UserRole | None = None
    state_user: bool | None = None


class UserResponse(UserBase):
    id_user: int

    model_config = ConfigDict(from_attributes=True)

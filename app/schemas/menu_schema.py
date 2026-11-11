from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class MenuBase(BaseModel):
    id_rest_menu: int
    name_menu: str = Field(min_length=1, max_length=100)
    price_menu: Decimal = Field(ge=0)
    state_menu: bool = True


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    id_rest_menu: int | None = None
    name_menu: str | None = Field(default=None, min_length=1, max_length=100)
    price_menu: Decimal | None = Field(default=None, ge=0)
    state_menu: bool | None = None


class MenuResponse(MenuBase):
    id_menu: int

    model_config = ConfigDict(from_attributes=True)
    
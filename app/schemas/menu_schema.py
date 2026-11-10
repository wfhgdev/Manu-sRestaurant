from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class MenuBase(BaseModel):
    id_rest_menu: int
    name_menu: str
    price_menu: Decimal
    state_menu: bool = True


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    id_rest_menu: int | None = None
    name_menu: str | None = None
    price_menu: Decimal | None = None
    state_menu: bool | None = None


class MenuResponse(MenuBase):
    id_menu: int

    model_config = ConfigDict(from_attributes=True)
    
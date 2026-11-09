
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class DishCreate(BaseModel):
    id_rest_dish: int
    id_cat_dish: int
    name_dish: str
    desc_dish: str | None = None
    price_dish: Decimal
    state_dish: bool = True
    allergen_ids: list[int] = []


class DishUpdate(BaseModel):
    id_rest_dish: int | None = None
    id_cat_dish: int | None = None
    name_dish: str | None = None
    desc_dish: str | None = None
    price_dish: Decimal | None = None
    state_dish: bool | None = None
    allergen_ids: list[int] | None = None


class DishResponse(BaseModel):
    id_dish: int
    id_rest_dish: int
    id_cat_dish: int
    name_dish: str
    desc_dish: str | None
    price_dish: Decimal
    state_dish: bool
    allergens: list[int]

    model_config = ConfigDict(from_attributes=True)

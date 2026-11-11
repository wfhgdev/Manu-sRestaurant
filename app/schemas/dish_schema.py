from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.allergen_schema import AllergenResponse

class DishCreate(BaseModel):
    id_rest_dish: int
    id_cat_dish: int
    name_dish: str = Field(min_length=1, max_length=100)
    desc_dish: str | None = None
    price_dish: Decimal = Field(ge=0)
    state_dish: bool = True
    allergen_ids: list[int] = []


class DishUpdate(BaseModel):
    id_rest_dish: int | None = None
    id_cat_dish: int | None = None
    name_dish: str | None = Field(default=None, min_length=1, max_length=100)
    desc_dish: str | None = None
    price_dish: Decimal | None = Field(default=None, ge=0)
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
    allergens: list[AllergenResponse]

    model_config = ConfigDict(from_attributes=True)

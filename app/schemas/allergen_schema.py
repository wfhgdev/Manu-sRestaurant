from pydantic import BaseModel, ConfigDict


class AllergenCreate(BaseModel):
    name_allergen: str


class AllergenUpdate(BaseModel):
    name_allergen: str


class AllergenResponse(BaseModel):
    id_allergen: int
    name_allergen: str

    model_config = ConfigDict(from_attributes=True)
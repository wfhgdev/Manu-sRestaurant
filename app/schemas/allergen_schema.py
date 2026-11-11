from pydantic import BaseModel, ConfigDict, Field


class AllergenCreate(BaseModel):
    name_allergen: str = Field(min_length=1, max_length=100)


class AllergenUpdate(BaseModel):
    name_allergen: str = Field(min_length=1, max_length=100)


class AllergenResponse(BaseModel):
    id_allergen: int
    name_allergen: str

    model_config = ConfigDict(from_attributes=True)
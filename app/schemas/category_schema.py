from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    id_rest_cat_rest: int
    name_cat_rest: str = Field(min_length=1, max_length=100)
    state_cat_rest: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    id_rest_cat_rest: int | None = None
    name_cat_rest: str | None = Field(default=None, min_length=1, max_length=100)
    state_cat_rest: bool | None = None


class CategoryResponse(CategoryBase):
    id_cat_rest: int

    model_config = ConfigDict(from_attributes=True)
    
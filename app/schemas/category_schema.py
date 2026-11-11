from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    id_rest_cat_rest: int
    name_cat_rest: str
    state_cat_rest: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    id_rest_cat_rest: int | None = None
    name_cat_rest: str | None = None
    state_cat_rest: bool | None = None


class CategoryResponse(CategoryBase):
    id_cat_rest: int

    model_config = ConfigDict(from_attributes=True)
    
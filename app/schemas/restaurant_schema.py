from pydantic import BaseModel, ConfigDict, Field


class RestaurantBase(BaseModel):
    cif_rest: str = Field(min_length=1, max_length=20)
    name_rest: str = Field(min_length=1, max_length=100)
    address_rest: str | None = Field(default=None, max_length=255)
    owner_rest: str | None = Field(default=None, max_length=100)
    tel_rest: str | None = Field(default=None, max_length=20)
    email_rest: str | None = Field(default=None, max_length=150)


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    cif_rest: str | None = Field(default=None, min_length=1, max_length=20)
    name_rest: str | None = Field(default=None, min_length=1, max_length=100)
    address_rest: str | None = Field(default=None, max_length=255)
    owner_rest: str | None = Field(default=None, max_length=100)
    tel_rest: str | None = Field(default=None, max_length=20)
    email_rest: str | None = Field(default=None, max_length=150)


class RestaurantResponse(RestaurantBase):
    id_rest: int

    model_config = ConfigDict(from_attributes=True)


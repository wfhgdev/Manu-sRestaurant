from pydantic import BaseModel, ConfigDict


class RestaurantBase(BaseModel):
    cif_rest: str
    name_rest: str
    address_rest: str | None = None
    owner_rest: str | None = None
    tel_rest: str | None = None
    email_rest: str | None = None


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    cif_rest: str | None = None
    name_rest: str | None = None
    address_rest: str | None = None
    owner_rest: str | None = None
    tel_rest: str | None = None
    email_rest: str | None = None


class RestaurantResponse(RestaurantBase):
    id_rest: int

    model_config = ConfigDict(from_attributes=True)


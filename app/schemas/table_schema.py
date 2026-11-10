from pydantic import BaseModel, ConfigDict, Field
from app.schemas.enums import TableLocation


class RestaurantTableBase(BaseModel):
    id_rest_table: int
    name_table: str = Field(min_length=1, max_length=100)
    cap_table: int = Field(gt=0)
    location_table: TableLocation
    state_table: bool = True


class RestaurantTableCreate(RestaurantTableBase):
    pass


class RestaurantTableUpdate(BaseModel):
    id_rest_table: int | None = None
    name_table: str | None = Field(default=None, min_length=1, max_length=100)
    cap_table: int | None = Field(default=None, gt=0)
    location_table: TableLocation | None = None
    state_table: bool | None = None


class RestaurantTableResponse(RestaurantTableBase):
    id_table: int

    model_config = ConfigDict(from_attributes=True)

from datetime import time
from pydantic import BaseModel, ConfigDict
from app.schemas.enums import ShiftName


class ShiftBase(BaseModel):
    id_rest_shift: int
    name_shift: ShiftName
    open_time_shift: time
    close_time_shift: time


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(BaseModel):
    id_rest_shift: int | None = None
    name_shift: ShiftName | None = None
    open_time_shift: time | None = None
    close_time_shift: time | None = None


class ShiftResponse(ShiftBase):
    id_shift: int

    model_config = ConfigDict(from_attributes=True)


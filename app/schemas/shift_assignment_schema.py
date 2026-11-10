from datetime import date, time
from pydantic import BaseModel, ConfigDict


class ShiftAssignmentBase(BaseModel):
    id_user_assign: int
    id_shift_assign: int
    date_assign: date
    actual_arrival_assign: time | None = None
    actual_departure_assign: time | None = None


class ShiftAssignmentCreate(ShiftAssignmentBase):
    pass


class ShiftAssignmentUpdate(BaseModel):
    id_user_assign: int | None = None
    id_shift_assign: int | None = None
    date_assign: date | None = None
    actual_arrival_assign: time | None = None
    actual_departure_assign: time | None = None


class ShiftAssignmentResponse(ShiftAssignmentBase):
    id_assign: int

    model_config = ConfigDict(from_attributes=True)


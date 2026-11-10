from datetime import date, datetime, time
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.enums import BookingState


class BookingBase(BaseModel):
    id_rest_booking: int
    name_client_booking: str = Field(min_length=1)
    date_booking: date
    start_time_booking: time
    qty_booking: int = Field(gt=0)
    state_booking: BookingState = BookingState.pendiente


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    id_rest_booking: int | None = None
    name_client_booking: str | None = Field(default=None, min_length=1)
    date_booking: date | None = None
    start_time_booking: time | None = None
    qty_booking: int | None = Field(default=None, gt=0)
    state_booking: BookingState | None = None


class BookingResponse(BookingBase):
    id_booking: int
    timestamp_booking: datetime

    model_config = ConfigDict(from_attributes=True)

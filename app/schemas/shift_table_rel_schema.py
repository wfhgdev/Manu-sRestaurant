from pydantic import BaseModel, ConfigDict


class ShiftTableRelBase(BaseModel):
    id_assign_shift_table_rel: int
    id_table_shift_table_rel: int


class ShiftTableRelCreate(ShiftTableRelBase):
    pass


class ShiftTableRelUpdate(BaseModel):
    id_assign_shift_table_rel: int | None = None
    id_table_shift_table_rel: int | None = None


class ShiftTableRelResponse(ShiftTableRelBase):
    id_shift_table_rel: int

    model_config = ConfigDict(from_attributes=True)


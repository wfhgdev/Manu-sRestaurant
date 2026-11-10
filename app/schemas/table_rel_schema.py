from pydantic import BaseModel, ConfigDict


class TableRelBase(BaseModel):
    id_booking_table_rel: int
    id_table_table_rel: int


class TableRelCreate(TableRelBase):
    pass


class TableRelUpdate(BaseModel):
    id_booking_table_rel: int | None = None
    id_table_table_rel: int | None = None


class TableRelResponse(TableRelBase):
    # table_rel no tiene id propio: cada fila se identifica por la pareja (reserva, mesa)
    model_config = ConfigDict(from_attributes=True)

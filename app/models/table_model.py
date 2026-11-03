from sqlalchemy import Integer, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database_connection import Base
from app.schemas.enums import TableLocation


class TableRelModel(Base):
    __tablename__ = "table_rel"

    id_booking_table_rel: Mapped[int] = mapped_column(Integer, ForeignKey("booking.id_booking"), primary_key=True)
    id_table_table_rel: Mapped[int] = mapped_column(Integer, ForeignKey("restaurant_table.id_table"), primary_key=True)


class RestaurantTableModel(Base):
    __tablename__ = "restaurant_table"

    id_table: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_rest_table: Mapped[int] = mapped_column(Integer, ForeignKey("restaurant.id_rest"), nullable=False)
    name_table: Mapped[str] = mapped_column(String(100), nullable=False)
    cap_table: Mapped[int] = mapped_column(Integer, nullable=False)
    location_table: Mapped[TableLocation] = mapped_column(
        SQLEnum(
            TableLocation,
            name="location_table_enum",
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False
        ),
        nullable=False
    )
    state_table: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    restaurant = relationship("RestaurantModel", back_populates="tables")
    bookings = relationship("BookingModel", secondary="table_rel", back_populates="tables")


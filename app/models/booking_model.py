from datetime import datetime, date, time
from sqlalchemy import Integer, String, Date, Time, DateTime, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database_connection import Base
from app.schemas.enums import BookingState


class BookingModel(Base):
    __tablename__ = "booking"

    id_booking: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_rest_booking: Mapped[int] = mapped_column(Integer, ForeignKey("restaurant.id_rest"), nullable=False)
    timestamp_booking: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    name_client_booking: Mapped[str] = mapped_column(String, nullable=False)
    date_booking: Mapped[date] = mapped_column(Date, nullable=False)
    start_time_booking: Mapped[time] = mapped_column(Time, nullable=False)
    qty_booking: Mapped[int] = mapped_column(Integer, nullable=False)
    state_booking: Mapped[BookingState] = mapped_column(
        SQLEnum(
            BookingState,
            name="booking_state_enum",
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False
        ),
        default=BookingState.pendiente,
        nullable=False
    )

    restaurant = relationship("RestaurantModel", back_populates="bookings")
    tables = relationship("RestaurantTableModel", secondary="table_rel", back_populates="bookings")


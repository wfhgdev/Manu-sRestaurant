from datetime import date, time
from sqlalchemy import Integer, Date, Time, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database_connection import Base
from app.schemas.enums import ShiftName


class ShiftModel(Base):
    __tablename__ = "shift"

    id_shift: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_rest_shift: Mapped[int] = mapped_column(Integer, ForeignKey("restaurant.id_rest"), nullable=False)
    name_shift: Mapped[ShiftName] = mapped_column(
        SQLEnum(
            ShiftName,
            name="shift_name_enum",
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False
        ),
        nullable=False
    )
    open_time_shift: Mapped[time] = mapped_column(Time, nullable=False)
    close_time_shift: Mapped[time] = mapped_column(Time, nullable=False)

    restaurant = relationship("RestaurantModel", back_populates="shifts")
    assignments = relationship("ShiftAssignmentModel", back_populates="shift", cascade="all, delete-orphan")


class ShiftAssignmentModel(Base):
    __tablename__ = "shift_assignment"

    id_assign: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_user_assign: Mapped[int] = mapped_column(Integer, ForeignKey("app_user.id_user"), nullable=False)
    id_shift_assign: Mapped[int] = mapped_column(Integer, ForeignKey("shift.id_shift"), nullable=False)
    date_assign: Mapped[date] = mapped_column(Date, nullable=False)
    actual_arrival_assign: Mapped[time | None] = mapped_column(Time, nullable=True)
    actual_departure_assign: Mapped[time | None] = mapped_column(Time, nullable=True)

    user = relationship("UserModel")
    shift = relationship("ShiftModel", back_populates="assignments")
    tables = relationship("RestaurantTableModel", secondary="shift_table_rel")


class ShiftTableRelModel(Base):
    __tablename__ = "shift_table_rel"

    id_shift_table_rel: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_assign_shift_table_rel: Mapped[int] = mapped_column(Integer, ForeignKey("shift_assignment.id_assign"), nullable=False)
    id_table_shift_table_rel: Mapped[int] = mapped_column(Integer, ForeignKey("restaurant_table.id_table"), nullable=False)


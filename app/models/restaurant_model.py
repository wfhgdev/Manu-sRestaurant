from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database_connection import Base


class RestaurantModel(Base):
    __tablename__ = "restaurant"

    id_rest: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cif_rest: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name_rest: Mapped[str] = mapped_column(String(100), nullable=False)
    address_rest: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owner_rest: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tel_rest: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email_rest: Mapped[str | None] = mapped_column(String(150), nullable=True)

    users = relationship("UserModel", back_populates="restaurant", cascade="all, delete-orphan")
    categories = relationship("CategoryModel", back_populates="restaurant", cascade="all, delete-orphan")
    dishes = relationship("DishModel", back_populates="restaurant", cascade="all, delete-orphan")
    menus = relationship("MenuModel", back_populates="restaurant", cascade="all, delete-orphan")
    tables = relationship("RestaurantTableModel", back_populates="restaurant", cascade="all, delete-orphan")
    bookings = relationship("BookingModel", back_populates="restaurant", cascade="all, delete-orphan")
    shifts = relationship("ShiftModel", back_populates="restaurant", cascade="all, delete-orphan")


from decimal import Decimal
from sqlalchemy import Integer, String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database_connection import Base


class MenuDetailModel(Base):
    __tablename__ = "menu_detail"

    id_menu_det: Mapped[int] = mapped_column(Integer, ForeignKey("menu.id_menu"), primary_key=True)
    id_dish_det: Mapped[int] = mapped_column(Integer, ForeignKey("dish.id_dish"), primary_key=True)


class MenuModel(Base):
    __tablename__ = "menu"

    id_menu: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_rest_menu: Mapped[int] = mapped_column(Integer, ForeignKey("restaurant.id_rest"), nullable=False)
    name_menu: Mapped[str] = mapped_column(String(100), nullable=False)
    price_menu: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    state_menu: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    restaurant = relationship("RestaurantModel", back_populates="menus")
    dishes = relationship("DishModel", secondary="menu_detail", back_populates="menus")


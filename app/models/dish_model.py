from decimal import Decimal
from sqlalchemy import Integer, String, Text, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database_connection import Base


class AllergenModel(Base):
    __tablename__ = "allergen"

    id_allergen: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_allergen: Mapped[str] = mapped_column(String(100), nullable=False)

    dishes = relationship("DishModel", secondary="rel_allergen", back_populates="allergens")


class RelAllergenModel(Base):
    __tablename__ = "rel_allergen"

    id_allergen_rel: Mapped[int] = mapped_column(Integer, ForeignKey("allergen.id_allergen"), primary_key=True)
    id_dish_rel: Mapped[int] = mapped_column(Integer, ForeignKey("dish.id_dish"), primary_key=True)


class DishModel(Base):
    __tablename__ = "dish"

    id_dish: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_rest_dish: Mapped[int] = mapped_column(Integer, ForeignKey("restaurant.id_rest"), nullable=False)
    id_cat_dish: Mapped[int] = mapped_column(Integer, ForeignKey("cat_rest.id_cat_rest"), nullable=False)
    name_dish: Mapped[str] = mapped_column(String(100), nullable=False)
    desc_dish: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_dish: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    state_dish: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    restaurant = relationship("RestaurantModel", back_populates="dishes")
    category = relationship("CategoryModel", back_populates="dishes")
    allergens = relationship("AllergenModel", secondary="rel_allergen", back_populates="dishes")
    menus = relationship("MenuModel", secondary="menu_detail", back_populates="dishes")


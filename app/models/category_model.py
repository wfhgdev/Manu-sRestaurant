from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database_connection import Base


class CategoryModel(Base):
    __tablename__ = "cat_rest"

    id_cat_rest: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_rest_cat_rest: Mapped[int] = mapped_column(Integer, ForeignKey("restaurant.id_rest"), nullable=False)
    name_cat_rest: Mapped[str] = mapped_column(String(100), nullable=False)
    state_cat_rest: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    restaurant = relationship("RestaurantModel", back_populates="categories")
    dishes = relationship("DishModel", back_populates="category", cascade="all, delete-orphan")


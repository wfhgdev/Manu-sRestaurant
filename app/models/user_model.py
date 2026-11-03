from sqlalchemy import Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database_connection import Base
from app.schemas.enums import UserRole


class UserModel(Base):
    __tablename__ = "app_user"

    id_user: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    id_rest_user: Mapped[int] = mapped_column(Integer, ForeignKey("restaurant.id_rest"), nullable=False, index=True)
    name_user: Mapped[str] = mapped_column(String(100), nullable=False)
    email_user: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    pass_user: Mapped[str] = mapped_column(String(255), nullable=False)
    role_user: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole,
            name="role_enum",
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False
        ),
        nullable=False
    )
    tel_user: Mapped[str | None] = mapped_column(String(20), nullable=True)

    restaurant = relationship("RestaurantModel", back_populates="users", lazy="select")

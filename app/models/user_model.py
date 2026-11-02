from sqlalchemy import Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database_connection import Base
from app.schemas.user_schema import UserRole


class UserModel(Base):
    __tablename__ = "app_user"

    id_user: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    id_rest_user: Mapped[int | None] = mapped_column(Integer, nullable=True)
    name_user: Mapped[str] = mapped_column(String, nullable=False)
    email_user: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    tel_user: Mapped[str | None] = mapped_column(String, nullable=True)
    pass_user: Mapped[str] = mapped_column(String, nullable=False)
    role_user: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole,
            name="role",
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False
        ),
        nullable=False
    )
    state_user: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

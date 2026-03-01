from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    role: Mapped[str] = mapped_column(String, default="user", nullable=False)  # "user" | "admin"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)






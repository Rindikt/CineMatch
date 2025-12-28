import enum
from datetime import date

from sqlalchemy import Integer, String, Enum, ForeignKey, CheckConstraint, Boolean, Date, func

from core.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


class WatchStatus(str, enum.Enum):
    PLANNED = "planned"      # Запланировано
    WATCHING = "watching"    # Смотрю
    COMPLETED = "completed"  # Просмотрено
    DROPPED = "dropped"      # Брошено


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    nickname: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role_enum", create_type=True),
        default=UserRole.user)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    movie_progress: Mapped[list["UserMovieProgress"]] = relationship(back_populates="user",
                                                                     cascade="all, delete-orphan")


class UserMovieProgress(Base):
    __tablename__ = "user_movie_progress"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)

    personal_rating: Mapped[int|None] = mapped_column(Integer, nullable=True)
    status: Mapped[WatchStatus] = mapped_column(
        Enum(WatchStatus),
        default=WatchStatus.PLANNED,
        nullable=False)

    user: Mapped['User'] = relationship(back_populates="movie_progress")
    movie: Mapped["Movie"] = relationship(back_populates="user_progress")

    __table_args__ = (
        CheckConstraint('personal_rating >= 1 AND personal_rating <= 10',name='check_rating_range'),
    )

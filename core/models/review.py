import enum
from datetime import datetime

from sqlalchemy import Text, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLAlchemyEnum

from core.db import Base



class ReviewType(enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    movie_id: Mapped[int] = mapped_column(ForeignKey('movies.id', ondelete='CASCADE'))

    review_text: Mapped[str] = mapped_column(Text, nullable=False)

    review_type: Mapped[ReviewType] = mapped_column(
        SQLAlchemyEnum(ReviewType),
        default=ReviewType.NEUTRAL,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped['User'] = relationship(back_populates="reviews")
    movie: Mapped["Movie"] = relationship(back_populates="reviews")

    @property
    def user_nickname(self):
        if self.user:
            return self.user.nickname
        return "Аноним"

    __table_args__ = (
        UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_review'),
    )
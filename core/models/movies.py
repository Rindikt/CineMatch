import decimal
from decimal import Decimal
import enum
from core.db import Base
from datetime import date, datetime
from sqlalchemy import Integer, ForeignKey, DECIMAL, PrimaryKeyConstraint, Enum, func, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship



class MediaType(str, enum.Enum):
    MOVIE = "movie"
    TV_SERIES = "tv"

class Movie(Base):
    __tablename__ = 'movies'
    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType, values_callable=lambda obj: [e.value for e in obj]),
                                                  nullable=False,
                                                  default=MediaType.MOVIE)
    number_of_seasons: Mapped[int|None]
    number_of_episodes: Mapped[int|None]
    title: Mapped[str]
    description: Mapped[str|None]
    tagline:Mapped[str|None]
    release_year: Mapped[int]
    release_date: Mapped[date|None]
    poster_path: Mapped[str|None]

    runtime_minutes: Mapped[int|None]
    rating: Mapped[float]
    popularity: Mapped[float]
    add_date: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    update_date_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    revenue: Mapped[Decimal|None] = mapped_column(DECIMAL(precision=20, scale=2), nullable=True)
    budget: Mapped[Decimal | None] = mapped_column(DECIMAL(precision=20, scale=2), nullable=True)
    user_progress: Mapped[list["UserMovieProgress"]] = relationship(back_populates="movie",
                                                                    cascade="all, delete-orphan")

    actors: Mapped[list['MovieActor']] = relationship(
        back_populates='movie',
        cascade='all, delete-orphan',
    )
    genres: Mapped[list['MovieGenre']] = relationship(
        back_populates='movie',
        cascade='all, delete-orphan'
    )


class Genre(Base):
    __tablename__ = 'genres'
    id: Mapped[int] = mapped_column(primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str]
    movies: Mapped[list['MovieGenre']] = relationship(
        back_populates='genre')


class MovieGenre(Base):
    __tablename__ = 'movie_genres'
    __table_args__ = (
        PrimaryKeyConstraint("movie_id", "genre_id"),
    )
    movie_id: Mapped[int] = mapped_column(ForeignKey('movies.id', ondelete='CASCADE'))
    genre_id: Mapped[int] = mapped_column(ForeignKey('genres.id', ondelete='CASCADE'))

    movie: Mapped['Movie'] = relationship(back_populates='genres')
    genre: Mapped['Genre'] = relationship(back_populates='movies')


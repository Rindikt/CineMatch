from datetime import date

from sqlalchemy import Integer, Date, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

class Actor(Base):
    __tablename__ = 'actors'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tmdb_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str]
    popularity: Mapped[float|None]
    profile_path: Mapped[str|None]
    biography: Mapped[str|None]
    birthday: Mapped[date|None] = mapped_column(Date, nullable=True)
    deathday: Mapped[date|None] = mapped_column(Date, nullable=True)

    movies: Mapped[list['MovieActor']] = relationship(
        back_populates='actor',
        cascade='all, delete-orphan')


class MovieActor(Base):
    __tablename__ = 'movie_actor'

    __table_args__ = (
        PrimaryKeyConstraint("actor_id", "movie_id"),
    )
    actor_id: Mapped[int] = mapped_column(Integer, ForeignKey('actors.id'), primary_key=True)
    movie_id: Mapped[int] = mapped_column(Integer, ForeignKey('movies.id'), primary_key=True)

    role_name: Mapped[str|None]

    actor: Mapped['Actor'] = relationship(
        back_populates='movies',
    )
    movie: Mapped['Movie'] = relationship(
        'Movie',
        back_populates='actors',
    )
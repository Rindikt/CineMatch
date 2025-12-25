from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, contains_eager

from core.models import Actor, MovieActor, Movie, MovieGenre, User, UserMovieProgress

PAGE_SIZE = 20

class ActorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_actor(self, actor_id: int):
        """
        Получает детальную информацию об актере по его внутреннему ID.
        """
        result = await self.db.scalar(select(Actor)
        .options(selectinload(Actor.movies).selectinload(MovieActor.movie))
        .where(Actor.id == actor_id))
        if result is None:
            raise ValueError(f'Актера с таким id: {actor_id} не найдено')
        return result


    async def get_actors(self, page):
        """
        Получает список актеров с поддержкой пагинации.
        """
        result = (await self.db.scalars(select(Actor).offset((page-1)* PAGE_SIZE))).all()
        if not result:
            raise ValueError('Актеров не найдено')
        return list(result)

    async def get_movies_by_actor(self, actor_id: int,
                                  current_user: Optional[User] = None):
        """
        Получает список всех фильмов, в которых участвовал актер, по его ID.
        """

        stmt = (
            select(Movie)
            .options(selectinload(Movie.genres).selectinload(MovieGenre.genre))
            .options(selectinload(Movie.actors))
            .join(MovieActor)
            .where(MovieActor.actor_id == actor_id)
            .distinct())

        if current_user:
            stmt = stmt.outerjoin(
                UserMovieProgress,
                (UserMovieProgress.movie_id == Movie.id) & (UserMovieProgress.user_id == current_user.id)
            ).options(contains_eager(Movie.user_progress))
        else:
            stmt = stmt.options(selectinload(Movie.user_progress))
        result = (await self.db.execute(stmt)).unique().scalars().all()


        if result is None:
            raise ValueError('Фильмов у данного актера не найдено')
        return list(result)

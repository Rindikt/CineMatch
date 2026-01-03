from math import ceil
from typing import Optional

from sqlalchemy import select, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, contains_eager

from core.models import Review
from core.models.movies import Movie
from core.models.actors import MovieActor
from core.models.movies import MovieGenre
from core.models.users import User as UserModel, UserMovieProgress, WatchStatus

SORT_FIELD_MAPPING = {
    'rating': Movie.rating,
    'release_year': Movie.release_year,
    'popularity': Movie.popularity,
    'title': Movie.title,
}

class MovieService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_movie(self, movie_id: int, current_user:Optional[UserModel]=None):
        """
        Получает детальную информацию о фильме по его внутреннему ID.
        Осуществляет вложенную загрузку связанных данных: актеров (с ролями)
        и жанров фильма.
        """
        stmt = select(Movie).where(Movie.id == movie_id)

        if current_user:
            stmt = stmt.outerjoin(
                UserMovieProgress,
                (UserMovieProgress.movie_id == Movie.id) &
                (UserMovieProgress.user_id == current_user.id)
            ).options(contains_eager(Movie.user_progress))
        else:
            stmt = stmt.options(selectinload(Movie.user_progress))

        stmt = stmt.options(
            selectinload(Movie.actors).selectinload(MovieActor.actor),
            selectinload(Movie.reviews).selectinload(Review.user),
            selectinload(Movie.genres).selectinload(MovieGenre.genre),

        )

        result = await self.db.execute(stmt)
        movie = result.unique().scalar_one_or_none()
        if not movie:
            raise ValueError(f'Фильм с id {movie_id} не найден')
        return movie

    async def get_movie_by_tmdb_id(self, tmdb_id: int):
        """
        Получает детальную информацию о фильме по его внешнему TMDb ID.
        Осуществляет вложенную загрузку связанных данных: актеров (с ролями)
        и жанров фильма.
        """
        movie = await self.db.scalar(
            select(Movie)
            .options(selectinload(Movie.actors).selectinload(MovieActor.actor),
                     selectinload(Movie.genres).selectinload(MovieGenre.genre), )
            .where(Movie.tmdb_id == tmdb_id)
        )
        if not movie:
            raise ValueError(f'Фильм с tmdb_id {tmdb_id} не найден')
        return movie

    async def get_movies_by_rating(self):
        """
        Получает список всех фильмов, отсортированных по рейтингу в порядке убывания.
        """
        movies = (await self.db.scalars(select(Movie).order_by(Movie.rating.desc()))).all()
        if not movies:
            raise ValueError('Фильмы отсутствуют')
        return list(movies)


    async def search_movie(self, search: str, page: int, page_size: int):
        """
        Осуществляет поиск фильмов по названию (по подстроке, без учета регистра).
        """
        pattern_search = f'%{search}%'
        base_stmt = select(Movie).where(Movie.title.ilike(pattern_search))

        count_stmt = select(func.count()).select_from(base_stmt.subquery())

        total_items = (await self.db.execute(count_stmt)).scalar_one()

        if total_items == 0:
            return {
                "items": [],
                "total_items": 0,
                "page": page,
                "pages": 0,
            }

        total_pages = ceil(total_items / page_size)

        if page > total_pages:
            page = total_pages

        final_stmt = base_stmt.options(
            selectinload(Movie.genres).selectinload(MovieGenre.genre),
            selectinload(Movie.actors),selectinload(Movie.user_progress)
        )

        final_stmt = final_stmt.order_by(desc(Movie.rating))
        final_stmt = final_stmt.distinct().offset((page - 1) * page_size).limit(page_size)

        result = (await self.db.scalars(final_stmt)).all()

        return {
            "items": list(result),
            "total_items": total_items,
            "page": page,
            "pages": total_pages,
        }

    async def get_movie_by_filter(self,
                                  genre_ids: str,
                                  year_max: int,
                                  sort_by: str,
                                  page: int,
                                  page_size: int,
                                  rating_min: float | None = None,
                                  year_min: int|None = None,
                                  direction: str = 'desc',
                                  current_user: Optional[UserModel]=None):
        """
        Получает список фильмов с применением множества фильтров, сортировки и пагинации.
        Фильтрует по диапазону лет, минимальному рейтингу и ID жанров
        """

        base_stmt = select(Movie)
        base_stmt = base_stmt.distinct()

        if current_user:
            base_stmt = base_stmt.outerjoin(UserMovieProgress,
                                            (UserMovieProgress.movie_id == Movie.id) & (UserMovieProgress.user_id == current_user.id)
                                            ).options(contains_eager(Movie.user_progress))

        if direction.lower() == 'asc':
            sort_direction = asc
        else:
            sort_direction = desc
        sort_by_filter = SORT_FIELD_MAPPING.get(sort_by, Movie.popularity)

        id_list = []

        if genre_ids is not None:
            try:
                id_list = [int(i.strip()) for i in genre_ids.split(',') if i.strip().isdigit()]
            except ValueError:
                pass

        if id_list:
            base_stmt = base_stmt.where(
                Movie.id.in_(
                    select(MovieGenre.movie_id).where(MovieGenre.genre_id.in_(id_list))
                )
            )
        filters = []
        if year_min and year_min > 0:
            filters.append(Movie.release_year >= year_min)

        if year_max:
            filters.append(Movie.release_year <= year_max)

        if rating_min is not None:
            filters.append(Movie.rating >= rating_min)

        if filters:
            base_stmt = base_stmt.where(*filters)

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_items = (await self.db.execute(count_stmt)).scalar_one()

        if total_items == 0:
            raise ValueError('Под ваши критерии фильмов не обнаружено')

        total_pages = ceil(total_items / page_size)

        if page > total_pages:
            page = total_pages

        final_stmt = base_stmt.options(
            selectinload(Movie.genres).selectinload(MovieGenre.genre)
        )
        if current_user:
            final_stmt = final_stmt.options(contains_eager(Movie.user_progress))
        else:
            final_stmt = final_stmt.options(selectinload(Movie.user_progress))

        if sort_by_filter is not None:
            final_stmt = final_stmt.order_by(sort_direction(sort_by_filter))
        else:
            final_stmt = final_stmt.order_by(desc(Movie.rating))

        final_stmt = final_stmt.offset((page - 1) * page_size).limit(page_size)

        result = (await self.db.scalars(final_stmt)).unique().all()
        if not result:
            raise ValueError('Под ваши критерии фильмов не обнаружено')
        return {
        "items": list(result),
        "total_items": total_items,
        "page": page,
        "pages": total_pages,
    }

    async def delete_movie_by_tmdb_id(self, tmdb_id: int):
        result = await self.db.scalar(select(Movie).where(Movie.tmdb_id==tmdb_id))
        if result is None:
            raise ValueError(f'Фильма с ID {tmdb_id} не найдено.')
        await self.db.delete(result)
        await self.db.commit()
        return {
            'message': f'Фильм с tmdb_id {tmdb_id} успешно удалён'
        }


    async def update_progress(self, movie_id: int,
                              current_user: UserModel,
                              status_movies: Optional[WatchStatus],
                              grade: Optional[int]):
        """
        Объединенное обновление статуса и оценки.
        """
        movie = await self.db.get(Movie, movie_id)
        if movie is None:
            raise ValueError('Фильм не найден')
        progress = await self.db.scalar(
            select(UserMovieProgress).where(
                UserMovieProgress.user_id == current_user.id,
                UserMovieProgress.movie_id == movie.id,
            ))

        if not progress:
            if not status_movies:
                raise ValueError('Необходимо выбрать статус')
            progress = UserMovieProgress(
                user_id=current_user.id,
                movie_id=movie.id,
                status=status_movies,
            )
            self.db.add(progress)
        else:
            if status_movies:
                progress.status = status_movies

        if grade is not None:
            if progress.status == WatchStatus.PLANNED:
                progress.personal_rating = None
            else:
                if not (1 <= grade <= 10):
                    raise ValueError('Оценка должна быть от 1 до 10')
                progress.personal_rating = grade
        else:
            progress.personal_rating = None
        await self.db.commit()
        await self.db.refresh(progress)
        return progress


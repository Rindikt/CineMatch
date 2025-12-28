from sqlalchemy import select, func, distinct, case, desc
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Genre, Movie, User as UserModel, MovieGenre, UserMovieProgress
from core.models.users import WatchStatus


class AnalyticsService:
    """
    Сервис для сбора и обработки аналитических данных приложения.

    Предоставляет статистику по фильмам, жанрам и пользователям для админ-панели.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_rating_users_in_genre(self):
        """
        Получает статистику просмотра фильмов и среднего рейтинга по жанрам от пользователей.
        """
        avg_user_rating = func.avg(UserMovieProgress.personal_rating).label('avg_rating')
        completed_views = func.count(
            case(
                (UserMovieProgress.status == WatchStatus.COMPLETED, UserMovieProgress.movie_id)
            )
        ).label('views_count')

        genre_res = await self.db.execute(select(Genre.name,
                                                 avg_user_rating,
                                                 completed_views)
                                          .join(MovieGenre, Genre.id == MovieGenre.genre_id)
                                          .join(Movie, Movie.id == MovieGenre.movie_id)
                                          .join(UserMovieProgress, Movie.id == UserMovieProgress.movie_id)
                                          .group_by(Genre.name))
        result = genre_res.mappings().all()
        genres_list = []
        rating_list = []
        for row in result:
            genres_list.append({
                "name": row['name'],
                "views_count": row['views_count'],
            })
            rating_list.append({
                "name": row['name'],
                "avg_rating": round(row['avg_rating'] or 0, 2),
            })
        return genres_list, rating_list


    async def get_top_movies_by_views(self, ):
        """
            Получает топ-10 фильмов по количеству завершенных просмотров.

            Для каждого фильма рассчитывается количество пользователей со статусом COMPLETED
            и средний пользовательский рейтинг.
        """

        avg_user_rating = func.avg(UserMovieProgress.personal_rating).label('avg_user_rating')
        completed_views = func.count(
            case(
                (UserMovieProgress.status == WatchStatus.COMPLETED, UserMovieProgress.movie_id)
            )
        ).label('views_count')

        result = await self.db.execute(select(Movie.title,
                                              completed_views,
                                              avg_user_rating)
                                       .join(UserMovieProgress, Movie.id == UserMovieProgress.movie_id)
                                       .group_by(Movie.id,Movie.title)
                                       .order_by(desc('views_count'))
                                       .limit(10))
        result = result.mappings().all()
        top_views_list = []
        top_ratings_list = []
        for row in result:
            top_views_list.append({
                "name": row['title'],
                "views_count": row['views_count'],
            })
            top_ratings_list.append({
                "name": row['title'],
                "user_rating": round(row['avg_user_rating'] or 0, 2),
            })

        return top_views_list, top_ratings_list

    async def get_data_in_genre(self):
        """
        Получает статистику распределения фильмов и среднего рейтинга по жанрам от tmdb.
        """

        genres_res = await self.db.execute(select(Genre.name,
                                                   func.count(distinct(Movie.id)).label('movie_count'),
                                                   func.avg(Movie.rating).label('avg_rating'),)
                                           .join(MovieGenre, Genre.id == MovieGenre.genre_id)
                                           .join(Movie, Movie.id == MovieGenre.movie_id)
                                            .group_by(Genre.name))
        result = genres_res.mappings().all()
        genres_list = []
        rating_list = []

        for row in result:
            genres_list.append({
                "name": row['name'],
                "movie_count": row['movie_count'],
            })
            rating_list.append({
                "name": row['name'],
                "avg_rating": round(row['avg_rating'] or 0, 2),
            })


        return genres_list, rating_list

    async def get_data_in_movies(self):
        """
        Получает динамику добавления фильмов за последние 14 дней и общее количество.
        """
        movie_res = await self.db.execute(select(Movie.add_date, func.count(Movie.id).label('movie_count'))
                                          .group_by(Movie.add_date)
                                          .order_by(Movie.add_date.desc())
                                          .limit(14))
        result = movie_res.mappings().all()
        movies_list = []
        for row in reversed(result):
            movies_list.append({
                "created_at": row['add_date'],
                "movie_count": row['movie_count'],
            })


        total_count = (await self.db.scalar(select(func.count(Movie.id).label('all_movie_count'))))

        return movies_list, (total_count or 0)

    async def get_data_in_users(self):
        """
        Получает динамику регистрации пользователей за последние 14 дней и общее количество.
        """
        user_res = await self.db.execute(select(UserModel.created_at, func.count(UserModel.id).label('users_count'))
                                         .group_by(UserModel.created_at)
                                         .order_by(UserModel.created_at.desc())
                                         .limit(14))
        result = user_res.mappings().all()
        users_list = []
        for row in reversed(result):
            users_list.append({
                "created_at": row['created_at'],
                "users_count": row['users_count'],
            })

        total_count = (await self.db.scalar(select(func.count(UserModel.id).label('total_user_count'))))

        return users_list, (total_count or 0)


    async def get_admin_stats(self):
        """
        Агрегирует все аналитические данные в единый отчет для фронтенда.
        Собирает общие счетчики и детальные списки для графиков (жанры, рейтинги, рост базы).
        """
        genres_list, rating_list = await self.get_data_in_genre()
        movies_list, total_movies = await self.get_data_in_movies()
        users_list, total_users = await self.get_data_in_users()
        views_list, user_rating_list = await self.get_rating_users_in_genre()
        top_views, top_ratings = await self.get_top_movies_by_views()

        return {
            "total_stats": {
             "total_movies": total_movies,
             "total_users": total_users,
            },
            "different_data":
            {
            "genres_list": genres_list,
            "rating_list": rating_list,
            "movies_list": movies_list,
            "users_list": users_list,
            "user_views_by_genre": views_list,
            "user_ratings_by_genre": user_rating_list,
            "top_10_views": top_views,
            "top_10_ratings": top_ratings,
            }
        }

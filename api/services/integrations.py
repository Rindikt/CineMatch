from contextlib import asynccontextmanager
from time import sleep
import asyncio
from typing import List
import asyncio

import httpx
from celery.bin.result import result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import *
from core.schemas.actors import ActorCreate
from core.schemas.genres import GenreBase

from core.integrations.tmdb_client import fetch_tmdb_data, fetch_popular_movie_ids
from core.integrations.movie_dto import transform_tmdb_movie

from core.integrations.actor_dto import transform_tmdb_actor
from core.integrations.genre_dto import transform_tmdb_genre
from worker.celery_app import celery_app

from core.db import async_session_maker



async def get_or_create_genre(session: AsyncSession, genre_data: GenreBase) -> Genre:
    """Ищет жанр по TMDB ID и создает, если не найден."""

    stmt = select(Genre).where(Genre.tmdb_id == genre_data.tmdb_id)
    result = await session.execute(stmt)
    genre = result.scalars().first()

    if genre:
        return genre

    new_genre = Genre(
        tmdb_id=genre_data.tmdb_id,
        name=genre_data.name
    )
    session.add(new_genre)
    await session.flush()
    return new_genre


async def get_or_create_actor(session: AsyncSession, actor_data: ActorCreate) -> Actor:
    """Ищет актера по TMDB ID и создает, если не найден."""
    stmt = select(Actor).where(Actor.tmdb_id == actor_data.tmdb_id)
    result = await session.execute(stmt)
    actor = result.scalars().first()

    if actor:
        return actor

    new_actor = Actor(**actor_data.model_dump())
    session.add(new_actor)
    await session.flush()
    return new_actor


async def import_movie_and_relations(tmdb_movie_id: int, session: AsyncSession = None):
    """Выполняет полную транзакцию импорта фильма, актеров и жанров."""

    print(f"--- 1. Starting Import for TMDB ID: {tmdb_movie_id} ---")

    raw_movie_data = await fetch_tmdb_data(f"/movie/{tmdb_movie_id}")
    movie_create_data = transform_tmdb_movie(raw_movie_data)
    raw_credits_data = await fetch_tmdb_data(f"/movie/{tmdb_movie_id}/credits")
    actors_data = []
    if raw_credits_data and raw_credits_data.get('cast'):
        for cast in raw_credits_data['cast'][:15]:
            tmdb_actor_id = cast.get('id')
            raw_actor_data = await fetch_tmdb_data(f"/person/{tmdb_actor_id}")
            actor_create_data = transform_tmdb_actor(raw_actor_data)
            actors_data.append({
                "info": actor_create_data,
                "character": cast.get('character')
            })

    if not movie_create_data:
        print("🛑 Failed to transform movie data.")
        return

    @asynccontextmanager
    async def get_session():
        if session:
            yield session
        else:
            async with async_session_maker() as new_session:
                yield new_session

    async with get_session() as active_session:
        try:

            genre_objects: List[Genre] = []
            raw_genres = raw_movie_data.get('genres', [])

            for raw_genre in raw_genres:
                genre_base = transform_tmdb_genre(raw_genre)
                if genre_base:
                    # Создаем или находим жанр в БД
                    genre_obj = await get_or_create_genre(active_session, genre_base)
                    genre_objects.append(genre_obj)

            print(f"--- 2. Saving Movie: {movie_create_data.title}...")

            movie_data = movie_create_data.model_dump(exclude={'genres_ids'})
            new_movie = Movie(**movie_data)

            active_session.add(new_movie)
            await active_session.flush()  # Получаем ID фильма (new_movie.id)

            # C. ОБРАБОТКА ЖАНРОВ (ЯВНАЯ АССОЦИАЦИЯ MovieGenre)
            print("--- 3. Processing Genres (Explicit Association) ---")
            for genre_obj in genre_objects:
                # ❗ Явное создание объекта MovieGenre для связи ❗
                movie_genre_link = MovieGenre(
                    movie=new_movie,
                    genre=genre_obj
                )
                active_session.add(movie_genre_link)

            # D. Обработка Актеров (Создание и Связывание через MovieActor)
            if raw_credits_data and raw_credits_data.get('cast'):
                print(f"--- 4. Processing cast members...")

                for item in actors_data:
                    actor_info = item['info']
                    character_name = item["character"]

                    if actor_info:
                        actor_obj = await get_or_create_actor(active_session, actor_info)

                        # Создание записи M2M (MovieActor)
                        movie_actor_link = MovieActor(
                            movie_id=new_movie.id,
                            actor_id=actor_obj.id,
                            role_name=character_name
                        )
                        active_session.add(movie_actor_link)

            await active_session.commit()
            print(f"✅ SUCCESSFULLY IMPORTED: {new_movie.title} (Movie ID: {new_movie.id})")

        except Exception as e:
            print(f"🛑 An error occurred during database transaction: {e}")
            await active_session.rollback()
            raise



async def run_initial_load(start_page: int, end_page: int):
    all_movies_ids = set()

    async with async_session_maker() as session:
        for page in range(start_page, end_page + 1):
            try:
                print(f"📡 Запрашиваем страницу {page} из {end_page}...")

                data = await fetch_popular_movie_ids(page)
                data_result = data.get("results", [])
                if not data_result:
                    print(f"⚠️ Страница {page} пуста. Завершаем.")
                    break
                current_page_ids = []

                for movie_data in data_result:
                    current_page_ids.append((movie_data['id']))

                    result = (await session.scalars(
                        select(Movie.tmdb_id)
                        .where(Movie.tmdb_id.in_(current_page_ids)))
                              ).all()
                    existing_ids = set(result)

                for movie_data in data_result:
                    if movie_data['id'] in existing_ids:
                        continue
                    else:
                        celery_app.send_task('worker.tasks.import_single_movie',
                                             kwargs={'tmdb_movie_id': movie_data['id']})
                all_movies_ids.update(current_page_ids)

            except Exception as e:
                await session.rollback()
                print(f"❌ Ошибка на странице {page}: {e}")

            await asyncio.sleep(1)

    print(f"Начальная загрузка завершена. Запущено задач для {len(all_movies_ids)} уникальных фильмов.")
    print(all_movies_ids)

async def update_movie_stats(tmdb_movie_id: int):
    """Обновляет только рейтинг и популярность фильма."""
    raw_data = await fetch_tmdb_data(f"/movie/{tmdb_movie_id}")
    if not raw_data:
        return

    async with async_session_maker() as session:
        try:
            movie = await session.scalar(
                select(Movie)
                .where(Movie.tmdb_id == tmdb_movie_id))
            if movie:
                movie.rating = raw_data['vote_average']
                movie.popularity = raw_data['popularity']
                await session.commit()
                print(f"✨ Stats updated for: {movie.title}")
        except Exception as e:
            print(f"🛑 Error updating stats for ID {tmdb_movie_id}: {e}")
            await session.rollback()


async def run_sync_oldest(batch_size: int):
        async with async_session_maker() as session:
            result = (await session.scalars(select(Movie).order_by(Movie.id.asc()).limit(batch_size))).all()
            if not result:
                raise ValueError('БД пуста, фильмов нет.')

            for movie_data in result:
                celery_app.send_task(
                    'worker.tasks.update_single_movie_stats',
                kwargs={'tmdb_movie_id': movie_data.tmdb_id})
        print(f"🔄 Отправлено на обновление: {len(result)} фильмов.")

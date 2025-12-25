from typing import List
import asyncio
from sentry_sdk.integrations import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import *
from core.schemas.movies import MovieCreate
from core.schemas.actors import ActorCreate
from core.schemas.genres import GenreBase
from core.integrations.tmdb_client import fetch_tmdb_data

from core.integrations.tmdb_client import fetch_tmdb_data
from core.integrations.movie_dto import transform_tmdb_movie

from core.integrations.actor_dto import transform_tmdb_actor
from core.integrations.genre_dto import transform_tmdb_genre

from core.db import async_session_maker


async def get_or_create_genre(session: AsyncSession, genre_data: GenreBase) -> Genre:
    """Ищет жанр по TMDB ID и создает, если не найден."""

    # Предполагаем, что у GenreBase есть поле .id для TMDB ID
    stmt = select(Genre).where(Genre.tmdb_id == genre_data.tmdb_id)
    result = await session.execute(stmt)
    genre = result.scalars().first()

    if genre:
        return genre

    # Создание (если не найден)
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

    # Создание
    new_actor = Actor(**actor_data.model_dump())
    session.add(new_actor)
    await session.flush()
    return new_actor

async def import_movie_and_relations(tmdb_movie_id: int):
    """Выполняет полную транзакцию импорта фильма, актеров и жанров."""

    print(f"--- 1. Starting Import for TMDB ID: {tmdb_movie_id} ---")

    # 1. Сбор данных (вне транзакции)
    raw_movie_data = await fetch_tmdb_data(f"/movie/{tmdb_movie_id}")
    movie_create_data = transform_tmdb_movie(raw_movie_data)

    raw_credits_data = await fetch_tmdb_data(f"/movie/{tmdb_movie_id}/credits")

    if not movie_create_data:
        print("🛑 Failed to transform movie data.")
        return

    async with async_session_maker() as session:
        try:

            genre_objects: List[Genre] = []
            raw_genres = raw_movie_data.get('genres', [])

            for raw_genre in raw_genres:
                genre_base = transform_tmdb_genre(raw_genre)
                if genre_base:
                    # Создаем или находим жанр в БД
                    genre_obj = await get_or_create_genre(session, genre_base)
                    genre_objects.append(genre_obj)

            # B. Сохранение Фильма
            print(f"--- 2. Saving Movie: {movie_create_data.title}...")

            movie_data = movie_create_data.model_dump(exclude={'genres_ids'})
            new_movie = Movie(**movie_data)

            # Мы не используем new_movie.genres.extend() здесь!

            session.add(new_movie)
            await session.flush()  # Получаем ID фильма (new_movie.id)

            # C. ОБРАБОТКА ЖАНРОВ (ЯВНАЯ АССОЦИАЦИЯ MovieGenre)
            print("--- 3. Processing Genres (Explicit Association) ---")
            for genre_obj in genre_objects:
                # ❗ Явное создание объекта MovieGenre для связи ❗
                movie_genre_link = MovieGenre(
                    movie=new_movie,
                    genre=genre_obj
                )
                session.add(movie_genre_link)

            # D. Обработка Актеров (Создание и Связывание через MovieActor)
            if raw_credits_data and raw_credits_data.get('cast'):
                print(f"--- 4. Processing cast members...")

                for cast_member in raw_credits_data['cast'][:15]:
                    tmdb_actor_id = cast_member.get('id')

                    raw_actor_data = await fetch_tmdb_data(f"/person/{tmdb_actor_id}")
                    actor_create_data = transform_tmdb_actor(raw_actor_data)

                    if actor_create_data:
                        actor_obj = await get_or_create_actor(session, actor_create_data)

                        # Создание записи M2M (MovieActor)
                        movie_actor_link = MovieActor(
                            movie_id=new_movie.id,
                            actor_id=actor_obj.id,
                            role_name=cast_member.get('character')
                        )
                        session.add(movie_actor_link)

            await session.commit()
            print(f"✅ SUCCESSFULLY IMPORTED: {new_movie.title} (Movie ID: {new_movie.id})")

        except Exception as e:
            # Ошибка, которую вы видели ('movie'), будет поймана здесь
            print(f"🛑 An error occurred during database transaction: {e}")
            await session.rollback()


async def main():
    tmdb_ids = [
        550,
        27205,
        157336,
        13,
        680,
        19995,
        496243,
        8587,
        76341,
        299534,
        11,  # Звёздные войны: Новая надежда
        12,  # В поисках Немо
        1891,  # Бриолин
        19404,  # Времена года
        133093,  # Одержимость
        238,  # Крестный отец
        424,  # Список Шиндлера
        539,  # Отступники
        77,  # Помни
        497,  # Зеленая миля
        603,  # Матрица
        122917,  # Хоббит: Нежданное путешествие
        10681,  # Кровавый алмаз
        377,  # Бой с тенью
        455207,  # Шазам!
        10195,  # Голодные игры
        771,  # Дневник памяти
        671,  # 8 миля
        389,  # Охотник на оленей
        696,  # Достучаться до небес
        103,  # Рокки
        293670,  # Дэдпул
        49521,  # Лобстер
        105,  # Назад в будущее
        496243,  # Паразиты (Дубликат, заменил) -> 496243 был в оригинале. Заменим на: 549        # Дорога
        311,  # Завтрак у Тиффани
        300669,  # Лига справедливости
        19866,  # Кунг-фу Панда
        462,  # Охотники за привидениями
        64690,  # Эволюция Борна
        68718,  # Жизнь Пи
        414,  # Амели
        40065,  # История игрушек: Большой побег
        600,  # Бесславные ублюдки
        807,  # Пила: Игра на выживание
        155,  # Тёмный рыцарь
        700,  # Семь
        18,  # Пятый элемент
        19,  # Секретные материалы: Борьба за будущее
        20,  # Секретные материалы: Хочу верить
        21,  # Секретные материалы: Я верю
        22,
        ]

    for tmdb_id in tmdb_ids:
        print("\n" + "=" * 50)
        print(f"STARTING BATCH IMPORT FOR ID: {tmdb_id}")
        print("=" * 50)
        await import_movie_and_relations(tmdb_movie_id=tmdb_id)
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
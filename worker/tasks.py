import asyncio

from worker.celery_app import celery_app
from api.services.integrations import (
    import_movie_and_relations,
    run_initial_load,
    run_sync_oldest,
    update_movie_stats)
from core.integrations.tmdb_client import fetch_popular_movie_ids


async def _async_import_single_movie(tmdb_movie_id: int):
    """
    Асинхронная обертка для вызова импорта фильма.
    """
    await import_movie_and_relations(tmdb_movie_id)


@celery_app.task(name='worker.tasks.import_single_movie')
def import_single_movie(tmdb_movie_id: int):
    """
    Синхронная задача Celery для запуска асинхронной функции импорта.
    Эта задача будет вызываться ДРУГИМИ задачами.
    """
    print(f"Celery: Task received for TMDB ID: {tmdb_movie_id}")
    asyncio.run(_async_import_single_movie(tmdb_movie_id=tmdb_movie_id))



async def _async_import_popular_movie_id(page: int):
    """
    Асинхронно запрашивает список популярных фильмов с конкретной страницы TMDB
    и инициирует их дальнейшую обработку.
    """

    await fetch_popular_movie_ids(page=page)

@celery_app.task(name='worker.tasks.sync_popular_movies_by_page')
def sync_popular_movies_by_page(page: int):
    """
    Celery-задача для синхронизации списка популярных фильмов.
    Запрашивает указанную страницу (page) популярных фильмов из TMDB API
    и запускает процесс сохранения их ID или постановки задач на импорт.
    """
    print(f"Celery: Fetching popular movies IDs from TMDB page: {page}")
    asyncio.run(_async_import_popular_movie_id(page))


@celery_app.task(name='worker.tasks.initial_load')
def initial_load(start_page: int = 1, end_page: int = 5):
    """Задача для запуска начальной загрузки популярных фильмов."""
    asyncio.run(run_initial_load(start_page, end_page))


@celery_app.task(name='worker.tasks.sync_oldest_movies')
def sync_oldest_movies(batch_size: int = 50):
    """Находит фильмы, которые дольше всего не обновлялись, и запускает их апдейт."""
    asyncio.run(run_sync_oldest(batch_size))

@celery_app.task(name='worker.tasks.update_single_movie_stats')
def update_single_movie_stats(tmdb_movie_id: int):
    """
    Легкая задача: обновить только рейтинг и популярность.
    """
    asyncio.run(update_movie_stats(tmdb_movie_id))


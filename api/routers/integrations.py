

from fastapi import APIRouter, Query, HTTPException, status
from worker.tasks import (import_single_movie,
                          sync_popular_movies_by_page,
                          initial_load,
                          sync_oldest_movies,
                          update_single_movie_stats)
from api.services.movies import MovieService

router = APIRouter(
    prefix='/integrations',
    tags=['integrations']
)

@router.get('/test')
async def test(page: int):
    result = sync_popular_movies_by_page.delay(page=page)
    return {
        "message": f"The task of importing movie data from the TMDB page has been started: {page}.",
        "task_id": result.id,
        "status": "PENDING"
    }

@router.get('/pages/{page_number}', description='Добавление фильмов по странично с tmdb')
async def get_movies_by_pages(start_page: int = Query(ge=1, description='Начальная страница скачивания'),
                              end_page: int = Query(ge=2, description='Конечная страница скачивания')):
    if start_page > end_page:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Стартовая страница не может быть больше конечной")
    result = initial_load.delay(start_page=start_page, end_page=end_page)
    return {
        "message": f"Movie page task triggered for TMDB ID: {result.id}.",
        "task_id": result.id,
        "status": "PENDING"
    }

@router.get('/update_movies',description='Обновление давно не обновляемых фильмов с конца по указанному кол-ву')
async def update_movies(batch_size: int):
    result = sync_oldest_movies.delay(batch_size=batch_size)
    return {
        'message': f"Movies task triggered for TMDB ID: {result.id}.",
        'task_id': result.id,
        'status': 'PENDING'
    }

@router.get('/update_movie/{tmdb_movie_id}',description='Обновление одного фильма по tmdb_id')
async def update_movie(tmdb_movie_id: int):
    result = update_single_movie_stats.delay(tmdb_movie_id=tmdb_movie_id)
    return {
        'message': f"Movie task triggered for TMDB ID: {result.id}.",
        'task_id': result.id,
        'status': 'PENDING'
    }

@router.get('/{tmdb_movie_id}', description='Добовление фильма в бд по tmdb_id')
async def add_movie(tmdb_movie_id: int):
    result = import_single_movie.delay(tmdb_movie_id=tmdb_movie_id)
    return {
        "message": f"Movie import task triggered for TMDB ID: {tmdb_movie_id}.",
        "task_id": result.id,
        "status": "PENDING"
    }







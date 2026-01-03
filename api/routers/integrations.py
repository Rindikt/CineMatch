from fastapi import APIRouter, Query, HTTPException, status, Depends
from celery.result import AsyncResult

from core.models import User as UserModel
from worker.tasks import (import_single_movie,
                          initial_load,
                          sync_oldest_movies,
                          update_single_movie_stats)
from core.auth import get_current_admin

router = APIRouter(
    prefix='/integrations',
    tags=['integrations']
)


@router.get('/pages/{page_number}', description='Добавление фильмов по странично с tmdb')
async def get_movies_by_pages(start_page: int = Query(ge=1, description='Начальная страница скачивания'),
                              end_page: int = Query(ge=2, description='Конечная страница скачивания'),
                              _: UserModel = Depends(get_current_admin),):
    if start_page > end_page:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Стартовая страница не может быть больше конечной")
    result = initial_load.delay(start_page=start_page, end_page=end_page)
    return {
        "message": f"Movie page task triggered for TMDB ID: {result.id}.",
        "task_id": result.id,
        "status": "PENDING"
    }

@router.get('/update_movies',description='Обновление давно не обновляемых фильмов с конца по указанному кол-ву')
async def update_movies(batch_size: int, _: UserModel = Depends(get_current_admin)):
    result = sync_oldest_movies.delay(batch_size=batch_size)
    return {
        'message': f"Movies task triggered for TMDB ID: {result.id}.",
        'task_id': result.id,
        'status': 'PENDING'
    }

@router.get('/update_movie/{tmdb_movie_id}',description='Обновление одного фильма по tmdb_id')
async def update_movie(tmdb_movie_id: int, _: UserModel = Depends(get_current_admin)):
    result = update_single_movie_stats.delay(tmdb_movie_id=tmdb_movie_id)
    return {
        'message': f"Movie task triggered for TMDB ID: {result.id}.",
        'task_id': result.id,
        'status': 'PENDING'
    }
@router.get("/task_status/{task_id}")
async def get_task_status(task_id: str, _: UserModel = Depends(get_current_admin)):
    result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status, # PENDING, SUCCESS, FAILURE
        "result": result.result if result.ready() else None
    }

@router.get('/{tmdb_movie_id}', description='Добовление фильма в бд по tmdb_id')
async def add_movie(tmdb_movie_id: int, _: UserModel = Depends(get_current_admin)):
    result = import_single_movie.delay(tmdb_movie_id=tmdb_movie_id)
    return {
        "message": f"Movie import task triggered for TMDB ID: {tmdb_movie_id}.",
        "task_id": result.id,
        "status": "PENDING"
    }







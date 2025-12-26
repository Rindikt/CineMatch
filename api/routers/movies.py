from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_db
from api.services.movies import MovieService
from core.models import User as UserModel
from core.models.users import WatchStatus
from core.schemas.movies import MovieRead, MovieBase, MovieLight
from core.schemas.pagination import PaginatedResponse
from core.auth import get_current_admin, get_current_user, get_current_user_optional


router = APIRouter(
    prefix="/movies",
    tags=['movies']
)

@router.get('/filter', response_model=PaginatedResponse[MovieLight])
async def get_movie_filter(
        genre_ids: str|None = Query(None),
        year_min: int|None = Query(
        1888, ge=1888, description='Фильмы, выпущенные не ранее указанного года'),
        year_max: int|None = Query(None, description='Фильмы, выпущенные не позднее указанного года'),
        rating_min: float|None = Query(None,ge=1.0, le=10.0, description='Фильмы с рейтингом не ниже указанного.'),
        sort_by: str|None = Query(None, description='Поле для сортировки'),
        page: int = Query(1, ge=1, description='Номер страницы'),
        page_size: int = Query(20, description='Количество фильмов на странице.'),
        db: AsyncSession = Depends(get_db),
        sort_direction: str = Query('desc', description="Направление сортировки: 'asc' или 'desc'."),
        current_user: Optional[UserModel] = Depends(get_current_user_optional),
):
    movies_service = MovieService(db)
    try:
        result = await movies_service.get_movie_by_filter(genre_ids=genre_ids,
                                                    year_max=year_max,
                                                    year_min=year_min,
                                                    rating_min=rating_min,
                                                    sort_by=sort_by,
                                                    page=page,
                                                    page_size=page_size,
                                                    direction=sort_direction,
                                                    current_user=current_user
                                                    )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get('/search', response_model=PaginatedResponse[MovieLight])
async def get_movie_search(search: str = Query(min_length=1, description='Поиск по названию фильма'),
                           page: int = Query(1, ge=1, description='Номер страницы'),
                           page_size: int = Query(20, description='Количество фильмов на странице.'),
                           db: AsyncSession = Depends(get_db)):
    movies_service = MovieService(db)
    try:
        result = await movies_service.search_movie(search, page=page, page_size=page_size)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get('/{movie_id}', response_model=MovieRead)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db), current_user: Optional[UserModel] = Depends(get_current_user_optional)):
    movies_service = MovieService(db)
    try:
        result = await movies_service.get_movie(movie_id, current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/tmdb/{tmdb_id}', response_model=MovieRead)
async def get_movie_tmdb(tmdb_id: int, db: AsyncSession = Depends(get_db)):
    movies_service = MovieService(db)
    try:
        result = await movies_service.get_movie_by_tmdb_id(tmdb_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/', response_model=list[MovieBase])
async def get_movies(db: AsyncSession = Depends(get_db)):
    movies_service = MovieService(db)
    try:
        result = await movies_service.get_movies_by_rating()
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete('/{tmdb_movie_id}')
async def delete_movie(tmdb_movie_id: int, db: AsyncSession = Depends(get_db),
                       _: UserModel = Depends(get_current_admin)):
    movie_service = MovieService(db)
    try:
        result = await movie_service.delete_movie_by_tmdb_id(tmdb_movie_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post('/{movie_id}/progress')
async def update_movie_progress(movie_id: int,
                                payload: dict = Body(...),
                                db: AsyncSession = Depends(get_db),
                                current_user: UserModel = Depends(get_current_user)):
    """
    Универсальный роут для обновления статуса и оценки одним запросом.
    """
    movie_service = MovieService(db)
    status_movies = payload.get('status')
    grade = payload.get('personal_rating')
    try:
        watch_status = WatchStatus(status_movies) if status_movies else None
        result = await movie_service.update_progress(
            movie_id,
            current_user,
            watch_status,
            grade,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

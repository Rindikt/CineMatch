from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from api.services.genres import GenreService
from core.schemas.genres import GenreRead

from core.db import get_db
router = APIRouter(
    prefix="/genres",
    tags=["genres"]
)


@router.get('/', response_model=list[GenreRead])
async def get_genres(db: AsyncSession = Depends(get_db)):
    genre_service = GenreService(db)
    try:
        genres = await genre_service.get_all_genres()
        return genres
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.services.actors import ActorService
from core.auth import get_current_user_optional
from core.models import User as UserModel
from core.schemas.actors import ActorRead
from core.schemas.movies import MovieLight
from core.db import get_db

router = APIRouter(
    prefix='/actors',
    tags=['actors']
)

@router.get('/{actor_id}', response_model=ActorRead)
async def get_actor(actor_id: int, db: AsyncSession = Depends(get_db)):
    actor_service = ActorService(db=db)
    try:
        actor = await actor_service.get_actor(actor_id)
        return actor
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get('/{actor_id}/movies', response_model=list[MovieLight])
async def get_actor_movies(actor_id: int, db: AsyncSession = Depends(get_db),
                           current_user: Optional[UserModel] = Depends(get_current_user_optional)):
    actor_service = ActorService(db=db)
    try:
        result = await actor_service.get_movies_by_actor(actor_id, current_user)
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get('/', response_model=list[ActorRead])
async def get_actors(page: int = Query(1, ge=1, description='Номер страницы'), db: AsyncSession = Depends(get_db)):
    actor_service = ActorService(db=db)
    try:
        actors = await actor_service.get_actors(page)
        return actors
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

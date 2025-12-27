from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.services.actors import ActorService
from core.auth import get_current_user_optional
from core.models.users import User as UserModel, UserRole
from core.schemas.users import UserBase
from core.auth import get_current_user, get_current_admin
from core.schemas.actors import ActorRead
from core.schemas.movies import MovieLight
from api.services.users import UserService
from core.db import get_db

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.patch('/users/update/{email}')
async def update_user(email: str,
                      user_status: UserRole,
                      _: UserModel = Depends(get_current_admin),
                      db: AsyncSession = Depends(get_db)):
    """
    Изменяет статус пользователя.
    """
    user_service = UserService(db=db)
    try:
        result = await user_service.update_status_user(email, user_status)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get('/users', response_model=list[UserBase])
async def get_users(db: AsyncSession = Depends(get_db), _: UserModel = Depends(get_current_admin)):
    """
    Получает список пользоватей.
    """
    user_service = UserService(db=db)
    try:
        result = await user_service.get_users()
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

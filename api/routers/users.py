from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from core.models import User as UserModel
from core.schemas.users import UserRegister, UserProfileResponse
from api.services.users import UserService
from core.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post('/register')
async def create_user(user: UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Регистрирует нового пользователя.
    """
    user_service = UserService(db=db)
    try:
        result =  await user_service.register_user(user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=str(e))

@router.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    """
    Аутентифицирует пользователя и возвращает access_token и refresh_token.
    """
    user_service = UserService(db=db)
    try:
        result = await user_service.login_user(form_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"})


@router.get('/me', response_model=UserProfileResponse)
async def get_me(db: AsyncSession = Depends(get_db),
                 current_user: UserModel = Depends(get_current_user)):
    """
    Возвращает данные о текущем пользователе
    """
    user_service = UserService(db=db)
    try:
        result = await user_service.get_user_profile(current_user)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


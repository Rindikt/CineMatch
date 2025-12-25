from fastapi import APIRouter, Depends, HTTPException,status, Request
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


@router.post('/refresh')
async def refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Обновляет access_token, используя refresh_token из заголовка или тела.
    """
    user_service = UserService(db=db)
    # Предполагаем, что токен пришел в заголовке Authorization: Bearer <REFRESH_TOKEN>
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Refresh token missing")

    refresh_token = auth_header.split(" ")[1]

    try:
        new_tokens = await user_service.refresh_tokens(refresh_token)
        return new_tokens
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


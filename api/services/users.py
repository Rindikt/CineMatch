import jwt
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.auth import hash_password, verify_password, create_access_token, create_refresh_token
from core.config import settings
from core.models import User as UserModel, UserMovieProgress
from core.schemas.users import UserRegister


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user: UserRegister):
        """
        Регистрирует нового пользователя.
        """
        result = await self.db.scalar(
            select(UserModel).where(or_(UserModel.email == user.email, UserModel.nickname == user.nickname))
        )
        if result:
            raise ValueError('Пользователь с таким логином или email уже существует')

        new_user = UserModel(
            email=user.email,
            nickname=user.nickname,
            hashed_password=hash_password(user.password),
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def login_user(self, form_data: OAuth2PasswordRequestForm):
        """
        Аутентифицирует пользователя и возвращает access_token и refresh_token.
        """
        user = await self.db.scalar(
            select(UserModel).where(or_(
                UserModel.email == form_data.username,
                UserModel.nickname == form_data.username
            ))
        )
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise ValueError('Неверное имя пользователя или пароль')

        token_data = {'sub': user.email, 'role': user.role.value, 'id': user.id}

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                }

    async def get_user_profile(self, current_user: UserModel):
        user = await self.db.scalar(select(UserModel)
                                    .options(selectinload(UserModel.movie_progress)
                                             .joinedload(UserMovieProgress.movie))
                                    .where(UserModel.id == current_user.id))
        if user is None:
            raise ValueError("Ошибка, пользователь не найден")
        return user

    async def refresh_tokens(self, refresh_token: str):
        try:
            # Декодируем рефреш-токен
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("id")
            if not user_id:
                raise ValueError("Invalid token")

            user = await self.db.get(UserModel, user_id)
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")

            # Создаем новую пару токенов
            token_data = {'sub': user.email, 'role': user.role.value, 'id': user.id}
            return {
                'access_token': create_access_token(token_data),
                'refresh_token': create_refresh_token(token_data),
                'token_type': 'bearer',
            }
        except jwt.PyJWTError:
            raise ValueError("Token expired or invalid")




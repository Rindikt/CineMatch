from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import ClassVar


class Settings(BaseSettings):

    CELERY_BROKER_URL: str = Field('redis://redis:6379/0')
    CELERY_RESULT_BACKEND: str = Field('redis://redis:6379/0')
    REDIS_URL: str = Field('redis://redis:6379/0')
    TMDB_IMAGE_BASE_URL: ClassVar[str] = "https://image.tmdb.org/t/p/"
    POSTER_SIZE_LIGHT: ClassVar[str] = "w185"
    PROFILE_SIZE_LIGHT: ClassVar[str] = "w45"
    POSTER_SIZE_FULL: ClassVar[str] = "w780"
    PROFILE_SIZE_FULL: ClassVar[str] = "h632"
    ALGORITHM: str = 'HS256'
    SECRET_KEY: str = "super_secret_key_change_me_in_production"


    DB_URL: str = Field('postgresql+asyncpg://user:password@postgres:5432/cinematch_db')

    TMDB_API_KEY: str = Field(..., description="Ключ API для TMDB")


    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )


settings = Settings()

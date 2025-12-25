from datetime import date

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, computed_field
from core.config import settings

class ActorLight(BaseModel):
    """Минимальная схема актера (для использования в MovieRead)."""
    id: int
    name: str
    profile_path: str | None = None

    @computed_field()
    @property
    def profile_url(self)-> Optional[str]:
        """Возвращает полный URL фото актера с CDN TMDb."""
        if self.profile_path:
            return f"{settings.TMDB_IMAGE_BASE_URL}{settings.PROFILE_SIZE_LIGHT}{self.profile_path}"
        return None
    model_config = ConfigDict(from_attributes=True)

class ActorBase(BaseModel):
    """Базовые поля, необходимые для создания или обновления актера."""
    name: str = Field(..., min_length=1, max_length=50, description='Имя/Фамилия актера')
    biography: str|None = Field(None, max_length=10000, description='Биография актера')
    birthday: date|None = Field(None, description='День рождения')
    deathday: date|None = Field(None, description='Дата смерти')
    model_config = ConfigDict(from_attributes=True)


class ActorCreate(ActorBase):
    """Схема для создания нового актера."""
    tmdb_id: int
    popularity: float | None
    profile_path: str | None = None

class ActorRead(ActorBase):
    """Схема для возврата данных актера."""
    id: int
    tmdb_id: int
    popularity: float|None
    profile_path: str | None = None
    @computed_field()
    @property
    def profile_url(self)-> Optional[str]:
        """Возвращает полный URL фото актера с CDN TMDb."""
        if self.profile_path:
            return f"{settings.TMDB_IMAGE_BASE_URL}{settings.PROFILE_SIZE_FULL}{self.profile_path}"
        return None

    movies: list['MovieActorRead'] = Field(default_factory=list, description='Список фильмов актера')

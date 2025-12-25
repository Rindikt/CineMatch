from decimal import Decimal

from core.config import settings
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, computed_field
from core.models.movies import MediaType
from core.models.users import WatchStatus



class MovieGenreRead(BaseModel):
    """Схема для объекта ассоциации (Genre)"""
    genre: 'GenreBase'
    model_config = ConfigDict(from_attributes=True)


class MovieLight(BaseModel):
    """Минимальная схема фильма."""
    id: int
    title: str
    media_type: MediaType
    release_year: int
    rating: float
    poster_path: str | None = None
    user_progress: list['MovieProgressRead'] = Field(default_factory=list, exclude=True)


    @computed_field
    @property
    def poster_url(self) -> Optional[str]:
        """Возвращает полный URL постера с CDN TMDb."""
        if self.poster_path:
            return f"{settings.TMDB_IMAGE_BASE_URL}{settings.POSTER_SIZE_LIGHT}{self.poster_path}"
        return None

    @computed_field
    @property
    def display_rating(self) -> str:
        """Рейтинг, округленный до двух знаков после запятой (добавляем по запросу)"""
        return f"{self.rating:.2f}"

    genres: list[MovieGenreRead] = Field(default_factory=list, description='Список жанров')

    @computed_field
    @property
    def genre_names(self)->list[str]:
        return [g.genre.name for g in self.genres if g.genre]

    @computed_field
    @property
    def personal_status(self)->Optional[str]:
        if self.user_progress:
            return self.user_progress[0].status.value
        return None

    @computed_field
    @property
    def personal_rating(self) -> Optional[int]:
        if self.user_progress:
            return self.user_progress[0].personal_rating
        return None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class MovieActorRead(BaseModel):
    """Схема для объекта ассоциации (Actor+Role)"""
    role_name: str = Field(..., description='Роль актера в фильме')
    actor: 'ActorLight'
    model_config = ConfigDict(from_attributes=True)


class MovieBase(BaseModel):
    """Базовые поля фильма для создания/обновления."""
    title: str = Field(..., min_length=3, max_length=100)
    media_type: MediaType
    release_year: int
    release_date: date | None = None
    rating: float
    model_config = ConfigDict(from_attributes=True)

class MovieCreate(MovieBase):
    """Схема для создания нового фильма."""
    tmdb_id: int
    tagline: str | None = None
    description: str | None = Field(None, max_length=2000)
    runtime_minutes: int|None = None
    rating: float
    popularity: float
    number_of_seasons: str|None = None
    number_of_episodes: str|None = None
    poster_path: str | None = None
    revenue: Optional[Decimal] = None
    budget: Optional[Decimal] = None

    genres_ids: list[int] = Field(default_factory=list, description='ID жанров для связи')


class MovieRead(MovieBase):
    """Схема для возврата данных фильма."""
    id: int
    tmdb_id: int

    tagline: str|None = None
    description: str|None = None
    runtime_minutes: int|None = None

    # Рейтинги
    rating: float
    popularity: float
    revenue: float|None = None
    budget: float|None = None

    number_of_seasons: str|None = None
    number_of_episodes: str|None = None

    actors: list[MovieActorRead] = Field(default_factory=list, description='Актерский состав')
    genres: list[MovieGenreRead] = Field(default_factory=list, description='Список жанров')
    poster_path: str | None = None

    @computed_field
    @property
    def poster_url(self)->Optional[str]:
        """Возвращает полный URL постера с CDN TMDb."""
        if self.poster_path:
            return f"{settings.TMDB_IMAGE_BASE_URL}{settings.POSTER_SIZE_FULL}{self.poster_path}"
        return None


class MovieProgressRead(BaseModel):
    id: Optional[int] = None
    movie_id: Optional[int] = None
    status: WatchStatus
    personal_rating: int | None = Field(None, ge=1, le=10)

    movie: MovieBase
    model_config = ConfigDict(from_attributes=True,
                              populate_by_name=True)
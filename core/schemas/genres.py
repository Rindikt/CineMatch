from pydantic import BaseModel, Field, ConfigDict



class GenreBase(BaseModel):
    """Базовая схема для возврата жанра (только ID и название)."""
    name: str = Field(..., min_length=1, max_length=50, description='Название жанра')
    model_config = ConfigDict(from_attributes=True)
    tmdb_id: int

class GenreRead(GenreBase):
    """Схема для возврата данных жанра."""
    id: int
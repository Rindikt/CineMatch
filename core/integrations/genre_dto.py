# core/integrations/genre_dto.py

from typing import Dict, Any, Optional
from core.schemas.genres import GenreBase


def transform_tmdb_genre(tmdb_data: Dict[str, Any]) -> Optional[GenreBase]:
    """
    Преобразует сырой JSON жанра TMDb в Pydantic схему Genre.

    :param tmdb_data: Словарь с данными жанра от TMDb.
    :return: Объект GenreBase или None.
    """
    if not tmdb_data or 'id' not in tmdb_data or not tmdb_data.get('name'):
        return None

    return GenreBase(
        tmdb_id=tmdb_data['id'],
        name=tmdb_data['name']
    )
from datetime import date
from typing import Dict, Any, Optional
from core.schemas.actors import ActorCreate


def transform_tmdb_actor(tmdb_data: Dict[str, Any]) -> Optional[ActorCreate]:
    """
    Преобразует сырой JSON актера TMDb в Pydantic схему ActorCreate.
    """
    if not tmdb_data or 'id' not in tmdb_data:
        return None

    full_name = tmdb_data.get('name', 'N/A')

    profile_path = tmdb_data.get('profile_path')
    birthday_str = tmdb_data.get('birthday')
    deathday_str = tmdb_data.get('deathday')

    birthday = date.fromisoformat(birthday_str) if birthday_str else None
    deathday = date.fromisoformat(deathday_str) if deathday_str else None

    popularity = tmdb_data.get('popularity') or 0.0
    biography = tmdb_data.get('biography') or None

    return ActorCreate(
        tmdb_id=tmdb_data['id'],
        name=full_name,
        popularity=popularity,
        biography=biography,
        birthday=birthday,
        deathday=deathday,
        profile_path=profile_path,
    )
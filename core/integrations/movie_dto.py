from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Any, Dict
from core.schemas.movies import MovieCreate
from core.models.movies import MediaType


def transform_tmdb_movie(tmdb_data: Dict[str, Any]) -> Optional[MovieCreate]:
    """
    Преобразует JSON от TMDb в схему MovieCreate, очищая и маппируя поля.
    """
    if not tmdb_data or 'id' not in tmdb_data:
        return None
    release_date_str = tmdb_data.get('release_date') or tmdb_data.get('first_air_date', '')

    release_date_obj: date | None = None

    if release_date_str:
        try:
            release_datetime = datetime.strptime(release_date_str, '%Y-%m-%d')
            release_date_obj = release_datetime.date()
        except ValueError:
            pass

    if release_date_str and release_date_str != '':
        release_year = int(release_date_str.split('-')[0])
    else:
        release_year = 0

    raw_budget = tmdb_data.get('budget')
    budget_decimal = Decimal(raw_budget) if isinstance(raw_budget, int) and raw_budget > 0 else None
    raw_revenue = tmdb_data.get('revenue')
    revenue_decimal = Decimal(raw_revenue) if isinstance(raw_revenue, int) and raw_revenue > 0 else None

    media_type_str = tmdb_data.get('media_type') or ('tv' if tmdb_data.get('first_air_date') else 'movie')

    try:
        media_type = MediaType(media_type_str)
    except ValueError:
        media_type = MediaType.MOVIE

    rating = tmdb_data.get('vote_average') or 0.0
    popularity = tmdb_data.get('popularity') or 0.0
    runtime = tmdb_data.get('runtime') or None
    poster_path = tmdb_data.get('poster_path') or None

    genres_ids = [g['id'] for g in tmdb_data.get('genres', []) if isinstance(g, dict) and 'id' in g]
    return MovieCreate(
        tmdb_id=tmdb_data['id'],
        title=tmdb_data.get('title') or tmdb_data.get('name', 'N/A'),

        # Наши типы
        media_type=media_type,
        release_year=release_year,
        release_date = release_date_obj,

        # Опциональные поля
        budget = budget_decimal,
        revenue = revenue_decimal,
        description=tmdb_data.get('overview') or None,
        tagline=tmdb_data.get('tagline') or None,
        runtime_minutes=runtime,
        rating=rating,
        popularity=popularity,
        poster_path=poster_path
    )

import pytest
from unittest.mock import patch, AsyncMock
from api.services.integrations import import_movie_and_relations
from http import HTTPStatus

TMDB_FETCH_PATH = "core.integrations.tmdb_client.fetch_tmdb_data"


@pytest.mark.asyncio
async def test_import_movie_logic_direct(db_session):
    # Данные для заглушки (те же, что были)
    mock_movie = {"id": 100, "title": "Test Movie", "genres": [{"id": 1, "name": "Action"}]}
    mock_credits = {"cast": [{"id": 50, "character": "Hero"}]}
    mock_actor = {"id": 50, "name": "John Doe", "biography": "Bio"}

    async def side_effect_func(url):
        if "credits" in url: return mock_credits
        if "movie/100" in url: return mock_movie
        if "person/50" in url: return mock_actor
        return {}

    # Патчим fetch_tmdb_data там, где она лежит (например, в api.services.tmdb)
    with patch("api.services.integrations.fetch_tmdb_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = side_effect_func

        # 1. Вызываем функцию напрямую!
        await import_movie_and_relations(100, session=db_session)

        # 2. Проверяем базу через db_session
        from core.models import Movie, Actor
        from sqlalchemy import select

        # Проверяем фильм
        res = await db_session.execute(select(Movie).where(Movie.tmdb_id == 100))
        movie = res.scalar_one_or_none()
        assert movie is not None
        assert movie.title == "Test Movie"

        # Проверяем актера
        act_res = await db_session.execute(select(Actor).where(Actor.name == "John Doe"))
        assert act_res.scalar_one_or_none() is not None
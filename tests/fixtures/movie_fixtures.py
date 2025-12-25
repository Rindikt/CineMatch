import pytest

from core.models import Movie
from core.models.movies import MediaType


@pytest.fixture(scope="function")
async def test_movie(db_session):
    movies_data = [
        {"title": "Тёмный рыцарь", "release_year": 2008, "tmdb_id": 155, "rating": 8.5},
        {"title": "Бегущий человек", "release_year": 2025, "tmdb_id": 798645, "rating": 6.8},
        {"title": "Начало", "release_year": 2010, "tmdb_id": 27205, "rating": 8.3},
    ]

    db_movies = []
    for data in movies_data:
        movie = Movie(
            **data,
            media_type=MediaType.MOVIE,
            popularity=100,
            genres=[]
        )
        db_session.add(movie)
        db_movies.append(movie)
    await db_session.commit()

    for m in db_movies:
        await db_session.refresh(m)

    return db_movies


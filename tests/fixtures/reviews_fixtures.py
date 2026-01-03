import pytest

from core.models.review import ReviewType, Review


@pytest.fixture(scope="function")
async def review(test_movie, second_test_user, db_session):
    movie_id = test_movie[0].id

    review = Review(
        movie_id=movie_id,
        user_id=second_test_user.id,
        review_type=ReviewType.NEUTRAL,
        review_text=f'Review #{movie_id}',
    )
    db_session.add(review)
    await db_session.commit()
    await db_session.refresh(review)
    return review
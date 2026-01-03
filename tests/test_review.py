import pytest
from http import HTTPStatus

from pytest_lazyfixture import lazy_fixture

from core.models.review import ReviewType


@pytest.mark.parametrize(
    'user, expected_status',
    [
        (lazy_fixture('admin_client'), HTTPStatus.OK),
        (lazy_fixture('auth_client'), HTTPStatus.OK),
        (lazy_fixture('client'), HTTPStatus.UNAUTHORIZED)
    ]
)
async def test_create_reviews(test_movie, user, expected_status):
    movie_id = test_movie[0].id
    create_payload = {'review_text': f'Review #{movie_id}',
                      'review_type': ReviewType.NEUTRAL.value,}
    response = await user.post(f"/reviews/{movie_id}/reviews", json=create_payload)
    assert response.status_code == expected_status
    if response.status_code == HTTPStatus.OK:
        data = response.json()
        assert data['review_type'] == ReviewType.NEUTRAL.value
        assert data['review_text'] == f'Review #{movie_id}'


@pytest.mark.parametrize(
    'user, expected_status',
    [
        (lazy_fixture('admin_client'), HTTPStatus.OK),
        (lazy_fixture('auth_second_client'), HTTPStatus.OK),
        (lazy_fixture('auth_client'), HTTPStatus.FORBIDDEN),
        (lazy_fixture('client'), HTTPStatus.UNAUTHORIZED)

    ]
)
async def test_delete_reviews(test_movie, user, expected_status, review):
    movie_id = test_movie[0].id
    review_id = 1
    response = await user.delete(f"/reviews/{movie_id}/reviews?review_id={review_id}")
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'user, expected_status',
    [
        (lazy_fixture('admin_client'), HTTPStatus.BAD_REQUEST),
        (lazy_fixture('auth_second_client'), HTTPStatus.OK),
        (lazy_fixture('auth_client'), HTTPStatus.BAD_REQUEST),
        (lazy_fixture('client'), HTTPStatus.UNAUTHORIZED)

    ]
)
async def test_update_reviews(test_movie, user, expected_status, review):
    movie_id = test_movie[0].id
    review_data = {'review_text': f'New text',
                   'review_type': ReviewType.NEUTRAL.value,}
    response = await user.patch(f"/reviews/{movie_id}/reviews", json=review_data)
    assert response.status_code == expected_status
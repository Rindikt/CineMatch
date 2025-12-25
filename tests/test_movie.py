import pytest
from http import HTTPStatus

from pytest_lazyfixture import lazy_fixture

async def test_get_movies(client, test_movie):
    response = await client.get(f'/movies/?sort_by=rating&order=desc')
    assert response.status_code == HTTPStatus.OK

    data = response.json()

    inception = next(m for m in data if m['title'] == 'Начало')

    assert isinstance(inception['rating'], float)
    assert inception["rating"] == 8.3
    assert data[0]['title'] == "Тёмный рыцарь"
    assert data[-1]['title'] == "Бегущий человек"

@pytest.mark.parametrize(
    "movie_id, expected_status",
    [
        (1, HTTPStatus.OK), (9999, HTTPStatus.NOT_FOUND),
    ]
)
async def test_get_movie(client, test_movie, movie_id, expected_status):
    response = await client.get(f'/movies/{movie_id}')
    assert response.status_code == expected_status
    data = response.json()
    if expected_status == HTTPStatus.OK:
        assert data['title'] == "Тёмный рыцарь"

@pytest.mark.parametrize(
    'movie_id, status, personal_rating, expected_status',
    [
        (1, "planned", 8.5, HTTPStatus.OK),
        (1, "watching", 8.5, HTTPStatus.OK),
        (1, "completed", 9.0, HTTPStatus.OK),
        (1, "", 5.0, HTTPStatus.BAD_REQUEST),
        (999, "completed", 9.0, HTTPStatus.BAD_REQUEST),

    ],
    ids=["status_planned", "status_watching", "status_completed", "status_empty",'movie_missing']
)
async def test_progress_rating_movies(auth_client, test_movie, movie_id, status, expected_status, personal_rating):
    payload = {
        "status": status,
        "personal_rating": personal_rating
    }
    response = await auth_client.post(f'/movies/{movie_id}/progress', json=payload)
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.OK:
        data = response.json()
        assert data['status'] == status
        if data['status'] == "planned":
            assert data['personal_rating'] is None
        else:
            assert data['personal_rating'] == personal_rating


async def test_update_existing_progress(auth_client, test_movie):
    movie_id = test_movie[0].id
    first_payload = {"status": "watching", "personal_rating": 8.5}
    await auth_client.post(f'/movies/{movie_id}/progress', json=first_payload)

    updated_payload = {"status": "completed", "personal_rating": 5.5}
    response = await auth_client.post(f'/movies/{movie_id}/progress', json=updated_payload)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['status'] == "completed"
    assert data['personal_rating'] == 5.5

@pytest.mark.parametrize(
    'user, expected_status',
    [
        (lazy_fixture('admin_client'), HTTPStatus.OK),
        (lazy_fixture('auth_client'), HTTPStatus.FORBIDDEN),
        (lazy_fixture('client'), HTTPStatus.FORBIDDEN),
    ]
)
async def test_delete_movie_as_admin(auth_client, test_movie, user, expected_status):
    movie_id = test_movie[0].tmdb_id
    response = await user.delete(f'/movies/{movie_id}')
    assert response.status_code == expected_status
    if expected_status == HTTPStatus.OK:
        get_res = await auth_client.get(f'/movies/tmdb/{movie_id}')
        assert get_res.status_code == HTTPStatus.NOT_FOUND
    else:
        get_res = await auth_client.get(f'/movies/tmdb/{movie_id}')
        assert get_res.status_code == HTTPStatus.OK


import pytest
from http import HTTPStatus

from pytest_lazyfixture import lazy_fixture


async def test_register_user_success(client):
    new_user_data = {"nickname": "first_test_user",
                     "email": "test_user@mail.com",
                     "password": "testpassword"}
    response = await client.post("/users/register", json=new_user_data)
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["email"] == "test_user@mail.com"
    assert data["nickname"] == "first_test_user"

@pytest.mark.parametrize(
    "type_user, expected_status",
    [(lazy_fixture('client'), HTTPStatus.UNAUTHORIZED),
     (lazy_fixture('auth_client'), HTTPStatus.OK),]
)
async def test_profile(type_user, expected_status):
    response = await type_user.get("/users/me")
    assert response.status_code == expected_status


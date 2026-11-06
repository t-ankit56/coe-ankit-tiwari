import pytest

from leaves.tests.conftest import login_as
from leaves.tests.factories import DEV_PASSWORD


@pytest.mark.django_db
def test_me_without_logging_in_returns_401(api_client):
    response = api_client.get("/api/me")

    assert response.status_code == 401


@pytest.mark.django_db
def test_login_returns_the_same_user_details_as_me(api_client, people):
    login_response = api_client.post(
        "/api/login", {"email": "ankit@incubyte.co", "password": DEV_PASSWORD}, format="json"
    )
    me_response = api_client.get("/api/me")

    assert login_response.status_code == 200
    assert login_response.json() == me_response.json()
    assert login_response.json()["email"] == "ankit@incubyte.co"

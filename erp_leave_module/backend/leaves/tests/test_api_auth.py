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


@pytest.mark.django_db
def test_me_shows_the_approver_and_whether_i_am_an_approver(api_client, people):
    login_as(api_client, people.ankit)
    ankit_details = api_client.get("/api/me").json()
    login_as(api_client, people.priya)
    priya_details = api_client.get("/api/me").json()

    assert ankit_details["is_approver"] is False
    assert ankit_details["approver"] == {"name": "Priya Nair"}
    assert priya_details["is_approver"] is True
    assert priya_details["approver"] == {"name": "Rohan Verma"}


@pytest.mark.django_db
def test_login_sets_the_csrf_cookie(api_client, people):
    response = api_client.post(
        "/api/login", {"email": "ankit@incubyte.co", "password": DEV_PASSWORD}, format="json"
    )

    assert "csrftoken" in response.cookies


@pytest.mark.django_db
def test_login_with_a_wrong_password_returns_400(api_client, people):
    response = api_client.post(
        "/api/login", {"email": "ankit@incubyte.co", "password": "not-the-password"}, format="json"
    )

    assert response.status_code == 400
    assert response.json() == {"error": "Wrong email or password."}


@pytest.mark.django_db
def test_after_logout_me_returns_401(api_client, people):
    login_as(api_client, people.ankit)

    logout_response = api_client.post("/api/logout")

    assert logout_response.status_code == 204
    assert api_client.get("/api/me").status_code == 401

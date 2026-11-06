import pytest


@pytest.mark.django_db
def test_me_without_logging_in_returns_401(api_client):
    response = api_client.get("/api/me")

    assert response.status_code == 401

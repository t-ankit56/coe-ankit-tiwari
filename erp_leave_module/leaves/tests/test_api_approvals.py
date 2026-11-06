from datetime import date

import pytest

from leaves.tests.conftest import login_as
from leaves.tests.factories import make_leave


@pytest.mark.django_db
def test_deciding_an_unknown_request_returns_404(api_client, people):
    login_as(api_client, people.priya)

    response = api_client.post("/api/leaves/99999/approve")

    assert response.status_code == 404
    assert response.json() == {"error": "Leave request not found."}


@pytest.mark.django_db
def test_approving_returns_200_with_the_updated_request(api_client, people, holidays):
    leave = make_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27))
    login_as(api_client, people.priya)

    response = api_client.post(f"/api/leaves/{leave.id}/approve")

    assert response.status_code == 200
    assert response.json()["leave"]["id"] == leave.id
    assert response.json()["leave"]["status"] == "approved"


@pytest.mark.django_db
def test_deciding_an_already_decided_request_returns_409(api_client, people, holidays):
    leave = make_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27), status="approved")
    login_as(api_client, people.priya)

    response = api_client.post(f"/api/leaves/{leave.id}/approve")

    assert response.status_code == 409
    assert response.json() == {"error": "This request has already been decided."}

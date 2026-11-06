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


@pytest.mark.django_db
def test_a_different_approver_deciding_returns_403(api_client, people, holidays):
    leave = make_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27))
    login_as(api_client, people.rohan)

    response = api_client.post(f"/api/leaves/{leave.id}/approve")

    assert response.status_code == 403
    assert response.json() == {"error": "Only the assigned approver can decide this request."}


@pytest.mark.django_db
def test_rejecting_without_a_comment_returns_400(api_client, people, holidays):
    leave = make_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27))
    login_as(api_client, people.priya)

    response = api_client.post(f"/api/leaves/{leave.id}/reject", {"comment": "   "}, format="json")

    assert response.status_code == 400
    assert response.json() == {"error": "A comment is required to reject."}


@pytest.mark.django_db
def test_requester_sees_the_rejection_comment_in_my_leaves(api_client, people, holidays):
    leave = make_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27))
    login_as(api_client, people.priya)
    api_client.post(f"/api/leaves/{leave.id}/reject", {"comment": "Release day"}, format="json")

    login_as(api_client, people.ankit)
    my_leaves = api_client.get("/api/leaves").json()["leaves"]

    assert my_leaves[0]["status"] == "rejected"
    assert my_leaves[0]["decision_comment"] == "Release day"

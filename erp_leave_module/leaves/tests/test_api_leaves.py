import pytest

from leaves.tests.conftest import login_as

NEW_REQUEST = {
    "start_date": "2026-11-23",
    "end_date": "2026-11-27",
    "half_day": False,
    "reason": "Family trip",
}


@pytest.mark.django_db
def test_my_leaves_response_has_a_summary_and_a_list(api_client, people):
    login_as(api_client, people.ankit)

    response = api_client.get("/api/leaves")

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"summary", "leaves"}
    assert set(body["summary"].keys()) == {"days_taken", "pending_count"}
    assert body["leaves"] == []


@pytest.mark.django_db
def test_submitting_leave_returns_201_with_the_created_request(api_client, people, holidays):
    login_as(api_client, people.ankit)

    response = api_client.post("/api/leaves", NEW_REQUEST, format="json")

    assert response.status_code == 201
    leave = response.json()["leave"]
    assert set(leave.keys()) == {
        "id", "start_date", "end_date", "half_day", "days", "reason", "status",
        "approver_name", "decision_comment", "submitted_at",
    }
    assert leave["days"] == 4
    assert leave["status"] == "pending"
    assert leave["approver_name"] == "Priya Nair"

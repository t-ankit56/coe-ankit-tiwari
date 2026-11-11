from datetime import date

import pytest

from leaves.tests.conftest import login_as
from leaves.tests.factories import make_leave

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


@pytest.mark.django_db
def test_a_whitespace_only_reason_returns_400(api_client, people, holidays):
    login_as(api_client, people.ankit)

    response = api_client.post("/api/leaves", {**NEW_REQUEST, "reason": "   "}, format="json")

    assert response.status_code == 400
    assert "reason" in response.json()["error"]


@pytest.mark.django_db
def test_submitting_leave_without_logging_in_returns_401(api_client, people):
    response = api_client.post("/api/leaves", NEW_REQUEST, format="json")

    assert response.status_code == 401


@pytest.mark.django_db
def test_preview_returns_days_and_a_day_by_day_breakdown(api_client, people, holidays):
    login_as(api_client, people.ankit)

    response = api_client.get(
        "/api/leaves/preview", {"start_date": "2026-11-23", "end_date": "2026-11-27", "half": "false"}
    )

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"days", "breakdown", "overlap", "probation"}
    assert body["days"] == 4
    assert len(body["breakdown"]) == 5
    assert body["breakdown"][4] == {"date": "2026-11-27", "counts": 0, "label": "Thanksgiving, not counted"}
    assert body["overlap"] is None
    assert body["probation"] is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    "submitting_user, request_body, expected_message",
    [
        (
            "ankit",
            {**NEW_REQUEST, "start_date": "2026-11-20", "end_date": "2026-11-23"},
            "You already have leave on 2026-11-18-2026-11-20.",
        ),
        (
            "ankit",
            {**NEW_REQUEST, "start_date": "2026-11-24", "end_date": "2026-11-23"},
            "End date cannot be before start date.",
        ),
        ("rohan", NEW_REQUEST, "No approver is assigned to you."),
    ],
    ids=["overlap", "invalid dates", "missing approver"],
)
def test_overlap_invalid_dates_and_missing_approver_each_return_400(
    api_client, people, holidays, submitting_user, request_body, expected_message
):
    make_leave(people.ankit, date(2026, 11, 18), date(2026, 11, 20), status="approved")
    login_as(api_client, getattr(people, submitting_user))

    response = api_client.post("/api/leaves", request_body, format="json")

    assert response.status_code == 400
    assert response.json() == {"error": expected_message}


@pytest.mark.django_db
def test_submitting_leave_over_the_probation_limit_returns_201_because_it_is_only_a_warning(api_client, people, holidays):
    make_leave(people.aarav, date(2026, 11, 2), date(2026, 11, 2), status="approved")
    make_leave(people.aarav, date(2026, 11, 3), date(2026, 11, 3), status="approved", half_day=True)
    login_as(api_client, people.aarav)

    response = api_client.post(
        "/api/leaves",
        {"start_date": "2026-11-19", "end_date": "2026-11-20", "half_day": False, "reason": "Wedding"},
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["leave"]["status"] == "pending"


@pytest.mark.django_db
def test_preview_for_a_user_on_probation_includes_the_month_breakdown_and_a_suggestion(api_client, people, holidays):
    make_leave(people.aarav, date(2026, 11, 2), date(2026, 11, 2), status="approved")
    make_leave(people.aarav, date(2026, 11, 3), date(2026, 11, 3), status="approved", half_day=True)
    login_as(api_client, people.aarav)

    response = api_client.get("/api/leaves/preview", {"start_date": "2026-11-19", "end_date": "2026-11-20"})

    assert response.status_code == 200
    assert response.json()["probation"] == {
        "ok": False,
        "limit": 2,
        "months": [{"month": "2026-11", "used": 1.5, "requested": 2, "left": 0.5, "over": 1.5}],
        "suggestion": {"start_date": "2026-11-19", "end_date": "2026-11-19", "half_day": True},
    }

from datetime import date

import pytest

from leaves.exceptions import (
    CommentRequiredToReject,
    LeaveAlreadyDecided,
    LeaveRequestNotFound,
    NotTheAssignedApprover,
)
from leaves.models import LeaveRequest
from leaves.services.approval_service import approve_leave, list_waiting_approvals, reject_leave
from leaves.tests.factories import make_leave


@pytest.mark.django_db
def test_no_waiting_requests_gives_an_empty_list(people):
    assert list_waiting_approvals(people.priya) == []


@pytest.mark.django_db
def test_deciding_a_request_that_does_not_exist_is_refused(people):
    with pytest.raises(LeaveRequestNotFound):
        approve_leave(people.priya, 99999)


@pytest.mark.django_db
def test_approving_moves_a_pending_request_to_approved_and_records_when(people, holidays):
    leave = make_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27))

    decided = approve_leave(people.priya, leave.id)

    leave.refresh_from_db()
    assert decided.id == leave.id
    assert leave.status == "approved"
    assert leave.decided_at is not None


@pytest.mark.django_db
def test_rejecting_with_a_comment_moves_it_to_rejected_and_stores_the_comment(people, holidays):
    leave = make_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27))

    reject_leave(people.priya, leave.id, "Release day")

    leave.refresh_from_db()
    assert leave.status == "rejected"
    assert leave.decision_comment == "Release day"
    assert leave.decided_at is not None


@pytest.mark.django_db
def test_waiting_list_shows_only_my_pending_requests_sorted_by_start_date(people, holidays):
    december_24 = make_leave(people.ankit, date(2026, 12, 24), date(2026, 12, 28))
    november_23 = make_leave(people.aarav, date(2026, 11, 23), date(2026, 11, 23))
    december_7 = make_leave(people.ankit, date(2026, 12, 7), date(2026, 12, 8))
    make_leave(people.ankit, date(2026, 7, 8), date(2026, 7, 10), status="approved")
    make_leave(people.priya, date(2026, 11, 30), date(2026, 11, 30))  # assigned to Rohan

    waiting = list_waiting_approvals(people.priya)

    assert waiting == [november_23, december_7, december_24]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "decide",
    [
        lambda approver, leave_id: approve_leave(approver, leave_id),
        lambda approver, leave_id: reject_leave(approver, leave_id, "Too late"),
    ],
    ids=["approve", "reject"],
)
def test_a_request_that_was_already_decided_cannot_be_decided_again(people, holidays, decide):
    leave = make_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27), status="approved")

    with pytest.raises(LeaveAlreadyDecided):
        decide(people.priya, leave.id)

    leave.refresh_from_db()
    assert leave.status == "approved"


@pytest.mark.django_db
@pytest.mark.parametrize("blank_comment", ["", "   "])
def test_a_blank_or_whitespace_only_comment_is_refused(people, holidays, blank_comment):
    leave = make_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27))

    with pytest.raises(CommentRequiredToReject):
        reject_leave(people.priya, leave.id, blank_comment)

    leave.refresh_from_db()
    assert leave.status == "pending"


@pytest.mark.django_db
def test_only_the_assigned_approver_can_decide(people, holidays):
    leave = make_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27))

    with pytest.raises(NotTheAssignedApprover):
        approve_leave(people.aarav, leave.id)

    leave.refresh_from_db()
    assert leave.status == "pending"


@pytest.mark.django_db
def test_an_approver_cannot_decide_their_own_request(people, holidays):
    own_request = make_leave(people.priya, date(2026, 11, 23), date(2026, 11, 27))  # assigned to Rohan

    with pytest.raises(NotTheAssignedApprover):
        approve_leave(people.priya, own_request.id)


@pytest.mark.django_db
def test_only_the_assigned_approver_can_reject(people, holidays):
    leave = make_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27))

    with pytest.raises(NotTheAssignedApprover):
        reject_leave(people.aarav, leave.id, "Not my call")

    leave.refresh_from_db()
    assert leave.status == "pending"

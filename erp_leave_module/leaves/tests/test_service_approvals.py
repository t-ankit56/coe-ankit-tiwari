from datetime import date

import pytest

from leaves.exceptions import LeaveRequestNotFound
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

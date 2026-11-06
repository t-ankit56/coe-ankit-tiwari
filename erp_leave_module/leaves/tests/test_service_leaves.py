from datetime import date
from decimal import Decimal

import pytest

from leaves.models import LeaveRequest
from leaves.tests.factories import make_leave
from leaves.services.leave_service import list_my_leaves, preview_leave, submit_leave

TODAY = date(2026, 11, 6)


@pytest.mark.django_db
def test_new_user_with_no_requests_gets_an_empty_list_and_zero_summary(people):
    my_leaves = list_my_leaves(people.ankit, today=TODAY)

    assert my_leaves.leaves == []
    assert my_leaves.days_taken == 0
    assert my_leaves.pending_count == 0


@pytest.mark.django_db
def test_submitting_leave_creates_a_pending_request_with_the_profile_approver_and_counted_days(people, holidays):
    leave = submit_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27), False, "Family trip")

    saved = LeaveRequest.objects.get(id=leave.id)
    assert saved.status == "pending"
    assert saved.approver == people.priya
    assert saved.days == Decimal("4.0")
    assert saved.reason == "Family trip"


@pytest.mark.django_db
def test_my_leaves_lists_only_my_requests_newest_first(people, holidays):
    older = make_leave(people.ankit, date(2026, 7, 8), date(2026, 7, 10), status="approved")
    make_leave(people.aarav, date(2026, 11, 2), date(2026, 11, 2), status="approved")
    newer = make_leave(people.ankit, date(2026, 12, 24), date(2026, 12, 28))

    my_leaves = list_my_leaves(people.ankit, today=TODAY)

    assert my_leaves.leaves == [newer, older]


@pytest.mark.django_db
def test_summary_counts_approved_days_this_year_and_pending_requests(people, holidays):
    make_leave(people.ankit, date(2026, 7, 8), date(2026, 7, 10), status="approved")
    make_leave(people.ankit, date(2026, 10, 22), date(2026, 10, 23), status="approved")
    make_leave(people.ankit, date(2026, 6, 15), date(2026, 6, 15), status="rejected")
    make_leave(people.ankit, date(2026, 12, 24), date(2026, 12, 28))

    my_leaves = list_my_leaves(people.ankit, today=TODAY)

    assert my_leaves.days_taken == Decimal("5")
    assert my_leaves.pending_count == 1

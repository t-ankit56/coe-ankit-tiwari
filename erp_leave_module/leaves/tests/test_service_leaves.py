from datetime import date
from decimal import Decimal

import pytest

from leaves.exceptions import (
    EndDateIsBeforeStartDate,
    HalfDayNeedsASingleWorkingDay,
    LeaveOverlapsExistingLeave,
    NoApproverAssigned,
)
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


@pytest.mark.django_db
def test_preview_returns_days_and_breakdown_with_no_probation_status_for_regular_user(people, holidays):
    preview = preview_leave(people.ankit, date(2026, 11, 23), date(2026, 11, 27))

    assert preview.days == Decimal("4")
    assert len(preview.breakdown) == 5
    assert preview.probation is None
    assert preview.overlap is None


@pytest.mark.django_db
def test_submitting_overlapping_leave_is_refused_and_names_the_clashing_dates(people, holidays):
    existing = make_leave(people.ankit, date(2026, 11, 18), date(2026, 11, 20), status="approved")

    with pytest.raises(LeaveOverlapsExistingLeave) as refusal:
        submit_leave(people.ankit, date(2026, 11, 20), date(2026, 11, 23), False, "Trip")

    assert refusal.value.leave.id == existing.id
    assert "2026-11-18" in str(refusal.value)
    assert LeaveRequest.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    "start_date, end_date, half_day, expected_refusal",
    [
        (date(2026, 11, 24), date(2026, 11, 23), False, EndDateIsBeforeStartDate),
        (date(2026, 11, 23), date(2026, 11, 24), True, HalfDayNeedsASingleWorkingDay),
    ],
)
def test_submitting_invalid_dates_is_refused(people, holidays, start_date, end_date, half_day, expected_refusal):
    with pytest.raises(expected_refusal):
        submit_leave(people.ankit, start_date, end_date, half_day, "Trip")


@pytest.mark.django_db
def test_submitting_without_an_approver_is_refused(people, holidays):
    with pytest.raises(NoApproverAssigned):
        submit_leave(people.rohan, date(2026, 11, 23), date(2026, 11, 27), False, "Trip")

    assert LeaveRequest.objects.count() == 0


@pytest.mark.django_db
def test_preview_reports_the_clashing_leave_instead_of_refusing(people, holidays):
    existing = make_leave(people.ankit, date(2026, 11, 18), date(2026, 11, 20), status="approved")

    preview = preview_leave(people.ankit, date(2026, 11, 20), date(2026, 11, 23))

    assert preview.overlap.id == existing.id

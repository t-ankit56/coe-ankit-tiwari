from datetime import date
from decimal import Decimal

import pytest

from leaves.models import LeaveRequest
from leaves.services.leave_service import list_my_leaves, preview_leave, submit_leave

TODAY = date(2026, 11, 6)


@pytest.mark.django_db
def test_new_user_with_no_requests_gets_an_empty_list_and_zero_summary(people):
    my_leaves = list_my_leaves(people.ankit, today=TODAY)

    assert my_leaves.leaves == []
    assert my_leaves.days_taken == 0
    assert my_leaves.pending_count == 0

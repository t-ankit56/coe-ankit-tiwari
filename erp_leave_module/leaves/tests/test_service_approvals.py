from datetime import date

import pytest

from leaves.exceptions import LeaveRequestNotFound
from leaves.services.approval_service import approve_leave, list_waiting_approvals


@pytest.mark.django_db
def test_no_waiting_requests_gives_an_empty_list(people):
    assert list_waiting_approvals(people.priya) == []

import pytest
from django.db import IntegrityError, transaction

from leaves.models import Profile


@pytest.mark.django_db
def test_a_user_without_an_approver_is_allowed(people):
    assert people.rohan.profile.approver is None

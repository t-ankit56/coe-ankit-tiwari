import pytest
from django.db import IntegrityError, transaction



@pytest.mark.django_db
def test_a_user_without_an_approver_is_allowed(people):
    assert people.rohan.profile.approver is None


@pytest.mark.django_db
def test_a_user_cannot_be_their_own_approver(people):
    profile = people.ankit.profile
    profile.approver = people.ankit

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            profile.save()


@pytest.mark.django_db
def test_user_is_an_approver_only_if_someone_has_them_as_approver(people):
    assert people.priya.profile.is_approver is True
    assert people.ankit.profile.is_approver is False

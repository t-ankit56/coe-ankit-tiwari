import pytest
from django.contrib.auth.models import User
from django.core.management import call_command

from leaves.models import Holiday, LeaveRequest


def count_seeded_rows():
    return User.objects.count(), Holiday.objects.count(), LeaveRequest.objects.count()


@pytest.mark.django_db
def test_running_seed_twice_creates_the_same_users_holidays_and_requests():
    call_command("seed")
    after_first_run = count_seeded_rows()
    call_command("seed")
    after_second_run = count_seeded_rows()

    assert after_first_run == (4, 3, 6)
    assert after_second_run == after_first_run

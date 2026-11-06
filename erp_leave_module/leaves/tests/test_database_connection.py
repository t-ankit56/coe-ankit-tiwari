from datetime import date

import pytest

from leaves.models import Holiday


@pytest.mark.django_db
def test_database_connects_and_a_holiday_can_be_saved_and_read_back():
    Holiday.objects.create(date=date(2026, 11, 27), name="Thanksgiving")

    assert Holiday.objects.get(date=date(2026, 11, 27)).name == "Thanksgiving"

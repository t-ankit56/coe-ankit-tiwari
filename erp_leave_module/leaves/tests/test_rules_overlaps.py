from datetime import date

from leaves.rules import LeaveRecord, find_overlapping_leave


def make_record(start_date, end_date, status="approved", id=1):
    return LeaveRecord(id=id, start_date=start_date, end_date=end_date, half_day=False, status=status)


WEDNESDAY_TO_FRIDAY = make_record(date(2026, 11, 18), date(2026, 11, 20))


def test_no_existing_leave_means_no_overlap():
    assert find_overlapping_leave(date(2026, 11, 19), date(2026, 11, 19), []) is None


def test_returns_the_existing_leave_that_overlaps():
    overlapping = find_overlapping_leave(date(2026, 11, 19), date(2026, 11, 19), [WEDNESDAY_TO_FRIDAY])

    assert overlapping == WEDNESDAY_TO_FRIDAY

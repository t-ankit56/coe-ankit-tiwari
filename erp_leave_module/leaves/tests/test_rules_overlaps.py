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


def test_returns_only_the_clashing_leave_when_there_are_several():
    in_july = make_record(date(2026, 7, 8), date(2026, 7, 10), id=1)
    in_december = make_record(date(2026, 12, 24), date(2026, 12, 28), id=3)
    in_november = make_record(date(2026, 11, 18), date(2026, 11, 20), id=2)

    overlapping = find_overlapping_leave(
        date(2026, 11, 19), date(2026, 11, 20), [in_july, in_november, in_december]
    )

    assert overlapping == in_november

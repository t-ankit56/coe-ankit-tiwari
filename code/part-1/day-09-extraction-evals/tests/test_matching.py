from matching import amount_ok, check, date_ok, sender_ok


def test_sender_accepts_an_added_address():
    assert sender_ok("Priya Nair", "Priya Nair, 12 Park Road, Leeds")


def test_sender_ignores_case_and_rejects_another_name():
    assert sender_ok("Klaus Weber", "klaus weber")
    assert not sender_ok("Klaus Weber", "Alpenwerk")


def test_sender_none_is_wrong():
    assert not sender_ok("Klaus Weber", None)


def test_date_accepts_the_same_day_in_another_format():
    assert date_ok("2026-03-14", "14 March 2026")
    assert date_ok("2026-08-09", "Aug 9, 2026")


def test_date_rejects_another_day():
    assert not date_ok("2026-02-03", "2026-03-05")


def test_date_none_expected_requires_none():
    assert date_ok(None, None)
    assert not date_ok(None, "03/04/2026")
    assert not date_ok("2026-04-22", None)


def test_date_unparseable_is_wrong():
    assert not date_ok("2026-04-03", "03/04/2026")


def test_amount_none_expected_requires_none():
    assert amount_ok(None, None)
    assert not amount_ok(None, 500.0)
    assert amount_ok(1234.5, 1234.50)


def test_check_reports_each_exact_field():
    expected = {"sender": "A B", "date": None, "amount": 5.0, "currency": "USD", "reference": "X-1", "purpose": "p"}
    got = {"sender": "A B", "date": "2026-01-01", "amount": 5.0, "currency": "EUR", "reference": "X-1", "purpose": "q"}
    assert check(expected, got) == {"sender": True, "date": False, "amount": True, "currency": False, "reference": True}

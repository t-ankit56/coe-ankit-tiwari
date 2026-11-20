"""Field rules from criteria.md. Each function says whether one extracted field is correct."""
from datetime import datetime

DATE_FORMATS = ("%Y-%m-%d", "%d %B %Y", "%B %d, %Y", "%b %d, %Y")


def sender_ok(expected: str | None, got: str | None) -> bool:
    if expected is None or got is None:
        return expected == got
    return expected.lower() in got.lower()


def _day(text: str):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    return None


def date_ok(expected: str | None, got: str | None) -> bool:
    if expected is None or got is None:
        return expected == got
    parsed = _day(got)
    return parsed is not None and parsed == _day(expected)


def amount_ok(expected: float | None, got: float | None) -> bool:
    return expected == got


def currency_ok(expected: str | None, got: str | None) -> bool:
    return expected == got


def reference_ok(expected: str | None, got: str | None) -> bool:
    return expected == got


RULES = {
    "sender": sender_ok,
    "date": date_ok,
    "amount": amount_ok,
    "currency": currency_ok,
    "reference": reference_ok,
}


def check(expected: dict, got: dict) -> dict[str, bool]:
    """Result per exact field. `purpose` is judged separately (DeepEval)."""
    return {field: rule(expected[field], got[field]) for field, rule in RULES.items()}

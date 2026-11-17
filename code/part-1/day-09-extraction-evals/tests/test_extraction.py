"""Eval suite for extract(): one call per case, then a gate on the pass rate (see criteria.md)."""
import json
import os
import time
from pathlib import Path

import pytest

from extract import extract
from matching import check

ROOT = Path(__file__).parent.parent
PROMPT_VERSION = os.environ.get("PROMPT_VERSION", "v2")
PAUSE_SECONDS = 2  # between calls, to stay inside free-tier rate limits
PASS_RATE = 0.75  # 9 of 12 cases on the first real v2 run, see NOTES.md


@pytest.fixture(scope="session")
def outputs() -> list[dict]:
    """Extract every case once (no retries) and save the outcome to results/<version>.json."""
    cases = json.loads((ROOT / "cases.json").read_text())
    rows = []
    for i, case in enumerate(cases):
        if i:
            time.sleep(PAUSE_SECONDS)
        source = case["source"]
        if not source.endswith(".pdf"):
            source = (ROOT / source).read_text(encoding="utf-8")
        else:
            source = str(ROOT / source)
        got = extract(source, PROMPT_VERSION).model_dump()
        fields = check(case["expected"], got)
        rows.append({"id": case["id"], "expected": case["expected"], "got": got, "fields": fields, "passed": all(fields.values())})
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / f"{PROMPT_VERSION}.json").write_text(json.dumps(rows, indent=2) + "\n")
    return rows


def test_pass_rate(outputs):
    rate = sum(r["passed"] for r in outputs) / len(outputs)
    misses = [
        f"{r['id']}: {field} expected {r['expected'][field]!r}, got {r['got'][field]!r}"
        for r in outputs
        for field, ok in r["fields"].items()
        if not ok
    ]
    assert rate >= PASS_RATE, f"prompt {PROMPT_VERSION}: pass rate {rate:.2f} is under {PASS_RATE}\n" + "\n".join(misses)

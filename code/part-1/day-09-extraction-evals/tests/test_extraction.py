"""Eval suite for extract(): one call per case, then a gate on the pass rate (see criteria.md)."""
import json
import os
import time
from pathlib import Path

import pytest
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from extract import extract
from judge import GeminiJudge
from matching import check

ROOT = Path(__file__).parent.parent
PROMPT_VERSION = os.environ.get("PROMPT_VERSION", "v2")
PAUSE_SECONDS = 2  # between calls, to stay inside free-tier rate limits
PASS_RATE = 0.75  # 9 of 12 cases on the first real v2 run, see NOTES.md
PURPOSE_THRESHOLD = 0.85  # mean GEval score for `purpose`: 0.89 on the first real v2 run, see NOTES.md
REUSE_SAVED = os.environ.get("REUSE_SAVED") == "1"  # dev only: judge saved outputs without calling extract()


@pytest.fixture(scope="session")
def outputs() -> list[dict]:
    """Extract every case once (no retries) and save the outcome to results/<version>.json."""
    saved = ROOT / "results" / f"{PROMPT_VERSION}.json"
    if REUSE_SAVED:
        return json.loads(saved.read_text())
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
    saved.write_text(json.dumps(rows, indent=2) + "\n")
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


PURPOSE_STEPS = [
    "Compare the actual purpose with the expected purpose: do they describe the same thing?",
    "Penalise an identifier in the actual purpose (an invoice, order, ticket or purchase order number).",
    "Ignore differences in wording or level of detail. Penalise only a missing or extra detail that changes the meaning.",
]


def purpose_metric() -> GEval:
    return GEval(
        name="Purpose",
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.EXPECTED_OUTPUT],
        evaluation_steps=PURPOSE_STEPS,
        model=GeminiJudge(),
        threshold=0.5,
        async_mode=False,
    )


def test_purpose_score(outputs):
    metric = purpose_metric()
    rows = []
    for i, r in enumerate(outputs):
        if i:
            time.sleep(PAUSE_SECONDS)
        case = LLMTestCase(
            input="Extract the purpose of the document.",
            actual_output=str(r["got"]["purpose"]),
            expected_output=r["expected"]["purpose"],
        )
        metric.measure(case)
        rows.append({"id": r["id"], "expected": r["expected"]["purpose"], "got": r["got"]["purpose"], "score": metric.score, "reason": metric.reason})
    (ROOT / "results" / f"{PROMPT_VERSION}-purpose.json").write_text(json.dumps(rows, indent=2) + "\n")
    mean = sum(r["score"] for r in rows) / len(rows)
    assert mean >= PURPOSE_THRESHOLD, f"prompt {PROMPT_VERSION}: mean purpose score {mean:.2f} is under {PURPOSE_THRESHOLD}"

"""Eval suite for answer(): one live run per case, judged by GEval, then a gate on the pass rate.

Needs the `evals` collection: `python service.py ingest evals/docs --collection evals`.
"""
import json
import os
import re
import time
from pathlib import Path

import pytest
from deepeval.test_case import LLMTestCase
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")  # keys, DATABASE_URL and LangSmith tracing

from judge import THRESHOLD, correctness_metric  # noqa: E402
from prompts import get_prompt  # noqa: E402
from service import answer, make_llm, make_store  # noqa: E402

PROMPT_VERSION = os.environ.get("PROMPT_VERSION", "v2")
PASS_RATE = 0.75  # v2 scored 4/4 on the first real run; one case below it, see NOTES.md
PAUSE_SECONDS = 5  # before every chat call: at most 12 a minute, under the free-tier 15 (Day 9 hit 429 at 2 s)
REUSE_SAVED = os.environ.get("REUSE_SAVED") == "1"  # local only: judge saved answers without calling answer()
COLLECTION = "evals"

CASES = json.loads((Path(__file__).parent / "cases.json").read_text())
SAVED = ROOT / "results" / f"{PROMPT_VERSION}.json"


def citations_ok(text: str, source_count: int) -> bool:
    """At least one [n], and every [n] points to a retrieved chunk."""
    cited = [int(n) for n in re.findall(r"\[(\d+)\]", text)]
    return bool(cited) and all(1 <= n <= source_count for n in cited)


def checks_for(case: dict, result: dict, judged: bool) -> dict:
    if case["expected_source"] is None:
        return {"unanswerable": judged}
    return {
        "source": case["expected_source"] in {s["document"] for s in result["sources"]},
        "citation": citations_ok(result["answer"], len(result["sources"])),
        "fact": judged,
    }


def run_answers() -> list[dict]:
    store, llm, prompt = make_store(COLLECTION), make_llm(), get_prompt()
    results = []
    for case in CASES:
        time.sleep(PAUSE_SECONDS)
        results.append(answer(case["question"], store, llm, prompt))
    return results


@pytest.fixture(scope="session")
def outputs() -> list[dict]:
    """Answer and judge every case once (no retries), save the outcome to results/<version>.json."""
    if REUSE_SAVED:
        results = [{k: row[k] for k in ("answer", "sources", "cost")} for row in json.loads(SAVED.read_text())]
    else:
        results = run_answers()
        # Save before judging, so a judge failure never throws away the generation calls.
        save([{"id": c["id"], "question": c["question"], **r} for c, r in zip(CASES, results)])
    metric = correctness_metric()
    rows = []
    for case, result in zip(CASES, results):
        time.sleep(PAUSE_SECONDS)
        metric.measure(LLMTestCase(input=case["question"], actual_output=result["answer"],
                                   expected_output=case["expected_fact"]))
        checks = checks_for(case, result, metric.score >= THRESHOLD)
        rows.append({"id": case["id"], "question": case["question"], "expected_source": case["expected_source"],
                     "expected_fact": case["expected_fact"], **result, "checks": checks,
                     "judge": {"score": metric.score, "reason": metric.reason}, "passed": all(checks.values())})
    save(rows)
    return rows


def save(rows: list[dict]) -> None:
    SAVED.parent.mkdir(exist_ok=True)
    SAVED.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")


def describe(row: dict) -> str:
    failed = [name for name, ok in row["checks"].items() if not ok]
    return f"{row['id']}: failed {', '.join(failed)}; judge {row['judge']['score']:.1f}: {row['judge']['reason']}"


@pytest.mark.parametrize("case_id", [c["id"] for c in CASES])
def test_case(outputs, case_id):
    """Reports each case. A failing case is xfailed with its reason, so only the pass rate gates the run."""
    row = next(r for r in outputs if r["id"] == case_id)
    if not row["passed"]:
        pytest.xfail(describe(row))


def test_pass_rate(outputs):
    rate = sum(r["passed"] for r in outputs) / len(outputs)
    misses = "\n".join(describe(r) for r in outputs if not r["passed"])
    assert rate >= PASS_RATE, f"prompt {PROMPT_VERSION}: pass rate {rate:.2f} is under {PASS_RATE}\n{misses}"

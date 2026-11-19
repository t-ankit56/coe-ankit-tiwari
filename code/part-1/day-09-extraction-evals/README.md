# Extraction evals

Spec: [SPEC.md](SPEC.md) · Criteria: [criteria.md](criteria.md) · Test set: [cases.json](cases.json) · Notes: [NOTES.md](NOTES.md)

An eval suite for the Day 7 `extract()` (copied here so the Day 7 submission stays untouched). It calls `extract()` once for each of 12 cases (10 emails, 2 PDFs), checks the five exact fields against the expected values, and passes when the share of passing cases is at or above `PASS_RATE`.

## How to run

```
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then put a Gemini API key in .env
pytest tests/test_matching.py                          # field rules, no API calls
PROMPT_VERSION=v2 pytest tests/test_extraction.py      # 12 live calls; v1 or v2
```

Each live run saves its outcome to [results/](results/) (`v1.json`, `v2.json`). Model: `gemini-3.1-flash-lite`, pinned, temperature 0. No retries, and a 2-second pause between calls.

## Results (Step 2)

24 live calls in total, once each: 12 for v1 and 12 for v2.

| Case | v1 | v2 |
| --- | --- | --- |
| `01-clean` | pass | pass |
| `02-missing` | pass | pass |
| `03-ambiguous` | fail: amount 500.0 (expected `None`) | pass |
| `04-meeting` | pass | pass |
| `05-two-amounts` | fail: date 15 June 2026 (expected 2026-06-30) | pass |
| `06-correction` | pass | pass |
| `07-date-format` | fail: date `03/04/2026` (expected `None`) | pass |
| `08-european-format` | pass | fail: sender "Alpenwerk" (expected Klaus Weber) |
| `09-card-charge` | pass | pass |
| `10-quote` | pass | pass |
| `invoice` | pass | fail: date 2026-03-05, the due date (expected 2026-02-03) |
| `invoice-hard` | pass | fail: date 2026-06-11, the due date (expected 2026-05-12) |
| **Pass rate** | **9/12 (75%)** | **9/12 (75%)** |

Both prompts score the same, so the pass rate alone does not separate them. v2 fixed three of v1's misses and caused three new ones (the same trade Day 7 recorded by hand). A gate on the rate catches a drop but not a swap of fixed and broken cases, so the per-case results in `results/` matter as much as the number. `PASS_RATE` is set to 0.75, the v2 result. With 12 cases, one case is about 8 points, and the output is probabilistic, so this is a small sample.

`purpose` is not scored yet. DeepEval judges it in Step 3.

## Judging `purpose` with DeepEval (Step 3)

`purpose` is free text, so a DeepEval `GEval` metric ([judge.py](judge.py) is a small Gemini judge, because DeepEval's default is a paid OpenAI model) scores whether it means the same as the expected purpose. The evaluation steps are in `PURPOSE_STEPS` in [tests/test_extraction.py](tests/test_extraction.py). `GEval` returns an integer from 0 to 10, rescaled to 0 to 1.

The judge was run once on the saved v2 outputs: 12 calls, using `REUSE_SAVED=1` so the extraction was not called again. Scores and reasons are in [results/v2-purpose.json](results/v2-purpose.json).

```
RUN_JUDGE=1 REUSE_SAVED=1 PROMPT_VERSION=v2 pytest tests/test_extraction.py::test_purpose_score
```

| Case | Got | Expected | Score |
| --- | --- | --- | --- |
| `01-clean` | annual software licence renewal | payment received for an annual software licence renewal | 1.0 |
| `02-missing` | delivery status inquiry | asking for the status of a delayed parcel | 0.9 |
| `03-ambiguous` | venue deposit | paying a venue deposit | 1.0 |
| `04-meeting` | project kickoff meeting | scheduling the project kickoff meeting | 1.0 |
| `05-two-amounts` | outstanding balance payment | asking for payment of the remaining balance | 1.0 |
| `06-correction` | conference booth fee | paying the conference booth fee | 1.0 |
| `07-date-format` | Training session | announcing a training session | 1.0 |
| `08-european-format` | invoice payment | paying an invoice | 1.0 |
| `09-card-charge` | order confirmation | a card charge for an order of one wireless mouse | **0.3** |
| `10-quote` | quotation for office chairs | quotation for 12 office chairs | **0.5** |
| `invoice` | payment for stationery supplies | supply of stationery (A4 paper and pens) | 1.0 |
| `invoice-hard` | payment for custom boxes and printed labels | supply of custom boxes and printed labels | 1.0 |
| **Mean** | | | **0.89** |

`PURPOSE_THRESHOLD` is 0.85, just under the mean, so a prompt that makes purposes clearly worse fails and one unlucky score does not.

**Judge against my hand judgement (Day 7):** it agrees on 10 of 12 cases. On `09` it is stricter than I was: "order confirmation" drops the card charge and the item, and I think the judge is right. On `10` it penalises the missing quantity of 12, which is stricter than the evaluation steps intend ("ignore level of detail"). So the score depends on how the steps are worded, and with 12 cases and an LLM judge it is a noisy number, not a fixed measurement.

## CI (Step 4)

[.github/workflows/evals.yml](../../../.github/workflows/evals.yml) runs the whole suite on every push and pull request: it installs `requirements.txt` on Python 3.14 and runs `pytest` from this folder, with `GEMINI_API_KEY` from the repository secrets (never printed). Each run makes 12 live calls (one extraction per case, no retries) and gates on the pass rate. The DeepEval judge test is skipped unless `RUN_JUDGE=1`; it can be switched on with the `run_judge` input of a manual run (`workflow_dispatch`), because 24 calls in one run go over the free-tier limit of 15 requests per minute. The check is named `extraction-evals`. Pull requests from forks do not receive repository secrets, so the key is empty there and the check fails.

**Runs: pending.** The workflow is committed, but no run has happened yet. The green run, the red run on a pull request that makes the v2 prompt worse, and the branch protection rule on `main` are still to be done and linked here. Until then CI is untested.

## Calls made

| What | Calls |
| --- | --- |
| Extraction on v1 (Step 2) | 12 |
| Extraction on v2 (Step 2) | 12 |
| DeepEval judge on the saved v2 outputs (Step 3) | 12 |
| **Total so far** | **36** |

Each CI run adds 12 more (24 on a manual run with `run_judge` on).

## Decisions

| Question | Decision |
| --- | --- |
| Why exact match for most fields? | The value is either right or wrong, so no judge is needed and the result is free and repeatable. |
| Why a judge only for `purpose`? | It is the one free-text field. A judge costs a call per case. |
| Why a Gemini judge? | DeepEval's default is a paid OpenAI model. The same free key is enough. |
| Why the Day 7 samples as the test set? | They already hold the edge cases, with expected values written before any run. |
| Why copy Day 7 and not import it? | The CI demo worsens the prompt, which must not touch the Day 7 submission. The cost is two copies that can drift. |
| Why live API calls in CI? | A saved output cannot show that a prompt change lowered accuracy. |
| Why a pass-rate threshold, not 100%? | The output is probabilistic. A threshold from the v2 result catches a drop without failing on noise. v1 and v2 both score 75%, so the gate catches a drop but not a swap of fixed and broken cases. |
| Why one assert on the rate, not one per case? | A per-case assert would turn CI red on any single miss and make the threshold meaningless. Per-case detail is in the failure message and `results/`. |
| Why `REUSE_SAVED`? | Judging the saved v2 outputs cost 12 judge calls instead of 24. It is dev only and CI never sets it. |
| Why no result caching otherwise? | The suite is 12 cases. Caching would hide the very change the suite is meant to catch. |

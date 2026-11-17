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

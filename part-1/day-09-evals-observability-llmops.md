# Part 1 · Day 9 — Evals, Observability & LLMOps

**Date completed:** 2026-11-20· **Time spent:** ~8 hours

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Explains why LLM features need evals | Yes | [Why LLM features need evals](#why-llm-features-need-evals) |
| Defines success criteria and a test set | Yes | [criteria.md](../code/part-1/day-09-extraction-evals/criteria.md) · [cases.json](../code/part-1/day-09-extraction-evals/cases.json) |
| Writes LLM tests with DeepEval | Yes | [judge.py](../code/part-1/day-09-extraction-evals/judge.py) · [GEval test](../code/part-1/day-09-extraction-evals/tests/test_extraction.py) · [scores](../code/part-1/day-09-extraction-evals/results/v2-purpose.json) |
| Traces calls and reads latency and cost | Yes | [tracing README](../code/part-1/day-09-rag-tracing/README.md#results) · [LangSmith run list](../code/part-1/day-09-rag-tracing/results/langsmith-runs.png) |
| Versions and tests prompt changes | Yes | [prompts.py](../code/part-1/day-09-extraction-evals/prompts.py) in git · [v1 and v2 results](../code/part-1/day-09-extraction-evals/README.md#results-step-2) |
| Runs evals in CI | Yes | [workflow](../.github/workflows/evals.yml) · [green run](https://github.com/t-ankit56/coe-ankit-tiwari/actions/runs/44608252061) · [CI section](../code/part-1/day-09-extraction-evals/README.md#ci-step-4) |

## Why LLM features need evals

An LLM's output is probabilistic: the same prompt can give a different answer on another day, with another model version, or after a small wording change, so I cannot read one good answer as proof that the feature works. A normal unit test gives a yes or no for one input. An eval runs a fixed set of real inputs, including the awkward ones, and scores them against expectations written before the run.

A single accuracy number also hides failures. Here prompts v1 and v2 both scored 9 of 12 cases, yet v2 had fixed three cases and broken three others. The number stayed the same, and the per-case results showed that the behaviour had changed. An eval is only useful if the test set has edge cases, the pass rule is written down first, and someone looks at which cases fail, not just how many.

## Key learnings

- **Success criteria first:** I wrote what counts as correct for each field, and the 12 expected values, before the first run. Writing it down forced decisions such as accepting a date in any format but never accepting a filled-in value where `None` is expected.
- **A rate hides swaps:** the pass rate was 75% for both prompts, so a gate on the rate catches a drop but not fixed cases traded for broken ones. Keeping the per-case results next to the number is what showed it.
- **A judge needs checking too:** the DeepEval judge scored `purpose` at 0.89 on average but disagreed with my own judgement on two cases, once stricter and right, once stricter than the steps intended. Its score depends on how the evaluation steps are worded.
- **Tracing shows where cost sits:** in the RAG flow `generate_answer` took about 65% of the time and 98% of the cost, mostly from the retrieved chunks in the prompt, and the database search was almost free.

## Exercises

### Practice: an eval suite for the Day 7 extraction function

Spec: [SPEC.md](../code/part-1/day-09-extraction-evals/SPEC.md) · Code and results: [README](../code/part-1/day-09-extraction-evals/README.md)

Success criteria and a 12-case test set (10 emails, 2 PDF invoices) were written before any run. A pytest suite calls `extract()` once per case, checks five fields against the expected values, and passes at or above a pass rate of 0.75. Prompts v1 and v2 both pass 9 of 12 cases: v2 fixed three of v1's misses and caused three new ones (both invoice dates and one sender). The rate alone does not separate them. See the [results](../code/part-1/day-09-extraction-evals/README.md#results-step-2).

### DeepEval: judge the `purpose` field

A `GEval` metric with a custom Gemini judge scored the saved v2 outputs at a mean of 0.89 (threshold 0.85). Two cases (`09` at 0.3 and `10` at 0.5) differ from my Day 7 hand judgment. See the [scores and comparison](../code/part-1/day-09-extraction-evals/README.md#judging-purpose-with-deepeval-step-3).

### Exercise 1: run the evals in CI

A GitHub Actions workflow runs the suite on every push and pull request, 12 live calls per run (the DeepEval judge is skipped unless switched on in a manual run, to stay under the free-tier rate limit). The [first run](https://github.com/t-ankit56/coe-ankit-tiwari/actions/runs/44608252061) failed on a Gemini 503 and passed when I re-ran it.


### Exercise 2: trace the Day 8 RAG flow

LangSmith spans on `embed_query`, `vector_search` and `generate_answer`, over the five Day 8 questions run once. `generate_answer` is the slowest step (about 1.02 s of 1.56 s) and the most expensive (about 98% of a cost of about $0.00015 per question, notional on the free tier). The Gemini embedding API returns no token count, so embedding tokens are an estimate.

## Reflection

I would refuse to ship any LLM feature whose output feeds something that matters, such as an amount or a date from an invoice, without an eval that runs on every prompt change. Also customer facing AI features should use eval because it might change their experience which can make UX bad.

## AI use

I used Claude Code (Sonnet 5.5) for this day. It wrote the spec, the success criteria, the test set, the matcher and the pytest suite, the DeepEval judge, the CI workflow, the tracing code, the READMEs and the notes. I asked for the spec first, approved each step's plan and each batch of API calls before it ran, and committed myself.

## Changes after review

-

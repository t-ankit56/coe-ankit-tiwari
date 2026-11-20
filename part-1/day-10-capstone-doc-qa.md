# Part 1 · Day 10 — Capstone: Document Question Answering Service

**Date completed:** · **Time spent:**

## Success criteria

| Criterion | Done? | Evidence |
| --- | --- | --- |
| End-to-end QA service over PDFs | Yes | [service.py](../code/part-1/day-10-doc-qa-service/service.py) · [results with answers and sources](../code/part-1/day-10-doc-qa-service/results/v2.json) |
| Test-first with versioned prompts | Yes | `git log` (`test:` → `feat:` → `refactor:` per cycle) · [tests](../code/part-1/day-10-doc-qa-service/tests/) · [prompts.py](../code/part-1/day-10-doc-qa-service/prompts.py) · [v1 and v2 results](../code/part-1/day-10-doc-qa-service/README.md#eval-results) |
| Tests and evals in CI through a pull request | Yes | [workflow](../.github/workflows/day-10.yml) · [green run](https://github.com/t-ankit56/coe-ankit-tiwari/actions/runs/44705732112) · [CI section](../code/part-1/day-10-doc-qa-service/README.md#ci) |
| Reports cost per question | Yes | [Cost per question](../code/part-1/day-10-doc-qa-service/README.md#cost-per-question) |
| Presents design and eval results with an honest failure | | [Presentation notes](#presentation-notes) · [the failure](../code/part-1/day-10-doc-qa-service/README.md#eval-results) |
| Comprehensive reflection | | [Reflection](#reflection) |

## Exercise

### A document question answering service

Spec: [SPEC.md](../code/part-1/day-10-doc-qa-service/SPEC.md) · Code and results: [README](../code/part-1/day-10-doc-qa-service/README.md) · Decisions: [NOTES.md](../code/part-1/day-10-doc-qa-service/NOTES.md)

The service ingests PDFs into pgvector and answers with numbered source chunks and a notional cost. There are 18 offline tests, written in ZOMBIES order, and an eval suite judged by DeepEval that runs in CI on the pull request. v1 passed 0/4 cases and v2 passed 4/4, and the cost is about $0.00024 per question. See the [results](../code/part-1/day-10-doc-qa-service/README.md#eval-results).

## Presentation notes

_To write._

## Key learnings

_To write._

## Reflection

_To write._

## AI use

_To write._

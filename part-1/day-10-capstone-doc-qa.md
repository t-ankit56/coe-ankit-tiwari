# Part 1 · Day 10 — Capstone: Document Question Answering Service

**Date completed:** 2026-11-20 · **Time spent:** ~ 8 hours

## Success criteria

| Criterion | Done? | Evidence |
| --- | --- | --- |
| End-to-end QA service over PDFs | Yes | [service.py](../code/part-1/day-10-doc-qa-service/service.py) · [results with answers and sources](../code/part-1/day-10-doc-qa-service/results/v2.json) |
| Test-first with versioned prompts | Yes | `git log` (`test:` → `feat:` → `refactor:` per cycle) · [tests](../code/part-1/day-10-doc-qa-service/tests/) · [prompts.py](../code/part-1/day-10-doc-qa-service/prompts.py) · [v1 and v2 results](../code/part-1/day-10-doc-qa-service/README.md#eval-results) |
| Tests and evals in CI through a pull request | Yes | [workflow](../.github/workflows/day-10.yml) · [green run](https://github.com/t-ankit56/coe-ankit-tiwari/actions/runs/44705732112) · [CI section](../code/part-1/day-10-doc-qa-service/README.md#ci) |
| Reports cost per question | Yes | [Cost per question](../code/part-1/day-10-doc-qa-service/README.md#cost-per-question) |
| Presents design and eval results with an honest failure | Yes | [Presentation notes](#presentation-notes) · [the failure](../code/part-1/day-10-doc-qa-service/README.md#eval-results) |
| Comprehensive reflection | Yes | [Reflection](#reflection) |

## Exercise

### A document question answering service

Spec: [SPEC.md](../code/part-1/day-10-doc-qa-service/SPEC.md) · Code and results: [README](../code/part-1/day-10-doc-qa-service/README.md) · Decisions: [NOTES.md](../code/part-1/day-10-doc-qa-service/NOTES.md)

The service ingests PDFs into pgvector and answers with numbered source chunks and a notional cost. There are 18 offline tests, written in ZOMBIES order, and an eval suite judged by DeepEval that runs in CI on the pull request. v1 passed 0/4 cases and v2 passed 4/4, and the cost is about $0.00024 per question. See the [results](../code/part-1/day-10-doc-qa-service/README.md#eval-results).


## Key learnings

- **Quotas shape the design:** the free tier counts every embedded chunk as one request, 100 a minute. Three chapters (172 chunks) hit a 429, so the eval corpus became 2 pages. I had read "batches of 100" as 2 calls.
- **Fakes only test the shape you give them:** every unit test returned a plain string, but Gemini 3 returns a list of content blocks. The first live run crashed at the judge and threw away 8 calls. Test 18 now covers it, and the suite saves answers before judging.
- **A correct answer can still fail:** v1 got every fact right and still scored 0/4, because it never cited a source and it answered from outside the documents when it had no answer. The prompt, not the model, made the difference.
- **Few cases make a coarse gate:** with 4 cases one miss is 25 points, so `PASS_RATE` sits one case below the v2 result instead of at 1.0.


## Reflection

The time I spent in COE was a great learning experience. It was important as I understood the standard of code quality required in Incubyte as well as the technologies that I need to learn. It got me upto pace in the way of working. I am looking forward to learn ROR and get claude and temporal certification in the future. 

## AI use

I used Claude Code (Opus 5.5) for this day. It wrote the spec, the code and tests, the eval suite and judge, the CI workflow, the READMEs. I approved a plan before every step and every batch of live API calls before it ran.

Decisions I made:
- a DeepEval judge, running in CI
- a `workflow_dispatch` fallback
- rebuilding the collection on ingest instead of ingesting incrementally
- NCERT physics chapters as the eval corpus
- cutting the corpus to one PDF and then 2 pages to save quota
- `PASS_RATE` 0.75
- the v1 myopia case as the failure to present
- keeping the chunk text in `results/`


## Open questions


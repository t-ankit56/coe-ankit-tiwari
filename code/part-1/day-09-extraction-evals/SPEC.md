# Evals, Observability and LLMOps: Build Spec for Claude Code

Write an eval suite for the Day 7 extraction function and run it in CI so a prompt change that lowers accuracy blocks the merge. Then add tracing to the Day 8 RAG flow and find its slowest and most expensive step. This is for the Day 9 assessment, so the recorded results and the commit history matter as much as the final code.

Two projects, one per exercise:

- `code/part-1/day-09-extraction-evals/` (this folder, holds this spec): the criteria, test set, pytest and DeepEval suite, and prompt comparison.
- `code/part-1/day-09-rag-tracing/`: the Day 8 RAG flow with tracing added.

CI lives in `.github/workflows/evals.yml` at the repo root, because GitHub only reads workflows from there.

## Instructions for Claude Code

**Ground rules**

1. **Always use plan mode.** Before every step, enter plan mode. The plan names what you will write and which calls you will make. Write no files and make no API calls until the user approves the plan.
2. **Never commit.** Do not run `git add`, `git commit` or any other git command that changes state. Read-only commands such as `git status` and `git diff` are fine. The user makes every commit. After each step, give a suggested commit message, then wait. Never add a Claude attribution or `Co-Authored-By` trailer.
3. **One step at a time.** Stop after each step, show what changed and the suggested commit message, then wait for the user to say continue.
4. **Keep API calls to a minimum.** Every call must be named in the step's plan and approved, and the exact prompt text is shown before it is sent. No retries, no loops over extra inputs, no re-running to see if the answer changes. Save every output to a file and fill the README from the saved files.
5. **Never print or commit a key.** `GEMINI_API_KEY` and `LANGSMITH_API_KEY` are read from an untracked `.env`. Do not echo or log them. Only `.env.example` with placeholders is committed. In CI they are repository secrets.
6. **Never invent data.** Expected values are written from the samples before any run.
7. **Simplest real thing first.** Dependencies: `pytest`, `deepeval`, `google-genai`, `pydantic`, `python-dotenv`, and `langsmith` for the tracing project. No extra frameworks, no result caching, no custom reporting.
8. **Do not build ahead.** Write nothing for a step until its plan is approved.
9. **Keep notes.** Whenever a result changes a decision (threshold, metric, prompt), append one line to `NOTES.md`.
10. **Reflection, key learnings, the explanation of why LLM features need evals, and the AI use section are the user's.** Do not write them in the day file.

## Provider and models

- Google Gemini API, free tier, the same key as Days 7 and 8.
- Model under test: `gemini-3.1-flash-lite`, pinned, as in Day 7. Never `-latest`.
- DeepEval's default judge is OpenAI (paid), so the judge is a small custom `DeepEvalBaseLLM` that calls the same Gemini model. Confirm the DeepEval API against its docs before writing it.
- Tracing: LangSmith free tier (named in the curriculum). Needs a free account and `LANGSMITH_API_KEY`.

## Scope

Extraction evals:
- Success criteria written down (`criteria.md`)
- Test set `cases.json`: the 10 Day 7 emails and 2 PDFs with expected values written from the Day 7 expected-value tables
- A pytest suite: one test per case, one `extract()` call per case, the five exact fields checked
- A DeepEval `GEval` metric for `purpose` only (the one fuzzy field)
- The suite run on prompt v1 and prompt v2, to show it tells them apart
- A GitHub Actions workflow that runs the suite on every push and pull request

RAG tracing:
- Day 8 `rag.py` with spans around embed, search and generate
- The five Day 8 questions traced once, with latency, tokens and cost per step

## Design

**Success criteria** (`criteria.md`, written before any run):

| Field | Correct when |
| --- | --- |
| `sender`, `date`, `amount`, `currency`, `reference` | Exact match with the expected value, using the Day 7 marking rules. `None` is correct when the input does not state the value. Inventing a value where `None` is expected is a failure. |
| `purpose` | The DeepEval `GEval` score is at or above its threshold. Scored separately from the exact fields. |
| Suite | A case passes when all five exact fields are correct. The run passes at or above one `PASS_RATE` constant (set from the v2 result and recorded in `NOTES.md`). The `purpose` score is reported next to it and has its own threshold. |

**Test set shape** (`cases.json`): a list of `{id, source, expected}`, where `source` is an email file or a PDF path, and `expected` holds the six fields. The 12 cases are the Day 7 samples, so the edge cases (missing values, ambiguous dates, two amounts, correction, European format) are already in it.

**Day 7 code is copied, not imported.** The Day 7 submission stays untouched: the CI demo deliberately worsens the prompt, and that must never land in the Day 7 folder. The copy lives in this folder, and `extract()` loads `.env` from the working directory, so pytest runs from here.

**Prompt change tested like a code change:** prompts already live in `prompts.py` (the copy in this folder), in source control. v1 (bare) to v2 (complete) is the change. The suite runs on both and the accuracy difference is recorded. The prompt version under test is chosen by the `PROMPT_VERSION` environment variable, defaulting to `v2`, so CI tests the committed default.

**CI gate:** the workflow installs the dependencies, runs `pytest` in this folder with `GEMINI_API_KEY` from the repository secrets, and fails when the pass rate is under `PASS_RATE` or the `purpose` score is under its threshold. Each case is extracted once per run (a shared fixture) and both checks reuse that output. To prove it blocks, one demo pull request makes the default prompt worse and goes red. Branch protection on `main` requires the check, so a red run cannot merge. The workflow runs the live API (12 extraction calls plus 12 judge calls per run, 24 in all, no retries), because replaying saved outputs would not test a prompt change.

**Tracing:** `@traceable` spans named `embed_query`, `vector_search` and `generate_answer` inside a parent `answer` span. Token counts come from the Gemini response usage metadata. Cost is tokens multiplied by the pinned model's published paid price per million tokens, with the price and its source written in the README. The free tier charges nothing, so this is a notional cost, and the README says so. The five questions run once each, and the README tables the latency and cost per step and names the slowest and the most expensive.

## Folder layout

```
.github/workflows/evals.yml            # at the repo root
code/part-1/day-09-extraction-evals/
  SPEC.md
  README.md
  NOTES.md
  criteria.md
  cases.json
  requirements.txt
  pyproject.toml                       # pytest pythonpath = ["."]
  .env.example
  extract.py  prompts.py  schema.py    # copied from Day 7 (self-contained)
  samples/                             # copied from Day 7: emails and PDFs
  judge.py                             # Gemini judge for DeepEval
  tests/test_extraction.py
  results/                             # saved v1 and v2 runs
code/part-1/day-09-rag-tracing/
  README.md
  NOTES.md
  requirements.txt
  .env.example
  rag.py                               # Day 8 rag.py plus tracing
  docs/  questions.md                  # copied from Day 8
  results/                             # trace export and cost table
```

## Step 0: Setup

No API calls.

1. In `day-09-extraction-evals/`, create the `venv/`, install `pytest`, `deepeval`, `google-genai`, `pydantic`, `python-dotenv`, freeze to `requirements.txt`, add `pyproject.toml`.
2. Copy `extract.py`, `prompts.py`, `schema.py` and `samples/` from Day 7.
3. Write `.env.example` with a `GEMINI_API_KEY` placeholder. Confirm `.env` is ignored with `git check-ignore`.
4. Check `python -c "import deepeval, google.genai"`.

**Suggested commit message:** `chore: Day 9 extraction evals setup with copied Day 7 code`

## Step 1: Success criteria and test set

No API calls and no code.

1. Write `criteria.md` from the table above.
2. Write `cases.json` from the Day 7 expected-value tables, before anything is run.

**Suggested commit messages:** `docs: success criteria for the extraction evals`, `test: test set from the Day 7 samples with expected values`

## Step 2: pytest eval suite

1. `tests/test_extraction.py`: one parametrised test over `cases.json`. It reads `PROMPT_VERSION` (default `v2`), calls `extract(source, prompt_version)` once per case through a shared fixture, and compares the five exact fields. The `purpose` field is skipped here and checked in Step 3. A final check computes the pass rate and compares it with `PASS_RATE`.
2. **Named API calls:** 12 `generate_content` calls for v1 and 12 for v2. The user approves each run. Save the outputs under `results/`.
3. Record the v1 and v2 pass rates in the README. Set `PASS_RATE` from the v2 result and note why in `NOTES.md`.

**Suggested commit messages:** `test: eval suite for the extraction function`, `docs: v1 and v2 accuracy on the eval suite`

## Step 3: DeepEval for `purpose`

1. `judge.py`: a `DeepEvalBaseLLM` that calls the pinned Gemini model with temperature 0.
2. Add a `GEval` metric for `purpose` (criterion: same meaning as the expected purpose, no identifiers) to the test, as a DeepEval `LLMTestCase` over the same cases.
3. **Named API calls:** one judge call per case (12), on the same per-case outputs from the shared fixture, so the extraction is not called again. Show the judge prompt text to the user first.
4. Record the scores. If a score disagrees with a hand judgement, note it in `NOTES.md`.

**Suggested commit message:** `test: judge the purpose field with a DeepEval GEval metric`

## Step 4: CI that blocks a bad prompt

1. `.github/workflows/evals.yml`: on push and pull request with no `paths:` filter (a required check that a path filter skips never reports, and it would block unrelated pull requests), Python set up, working directory this folder, `pip install -r requirements.txt`, `pytest` with `GEMINI_API_KEY` from `secrets`.
2. The user adds the repository secret and, on `main`, a branch protection rule requiring the check. Claude gives the exact settings steps and does not touch the repository settings.
3. Demo: a branch that makes this folder's `prompts.py` v2 worse. Push it and record the red run, then the green run on the fix. Link both runs in the README.
4. Never print the key. Fork pull requests do not receive secrets, so note that in the README.

**Suggested commit messages:** `ci: run the extraction evals on every push and pull request`, `docs: CI runs showing a prompt regression blocked`

## Step 5: Tracing the Day 8 RAG flow

1. In `day-09-rag-tracing/`, create the `venv/`, install `google-genai`, `psycopg[binary]`, `python-dotenv` and `langsmith`, freeze to `requirements.txt`, and write `.env.example` (`GEMINI_API_KEY`, `DATABASE_URL`, `LANGSMITH_API_KEY`, `LANGSMITH_TRACING`). Copy Day 8 `rag.py`, `docs/` and `questions.md`. Add the `@traceable` spans from the design above.
2. **Named API calls:** the Day 8 `day8` database is reused. If it has no rows for chunk size 600, ingest it once (one embedding batch). Then 5 query embeddings and 5 answer calls, once each, plus LangSmith trace uploads.
3. Save the latency, token and cost numbers for each step in `results/`, and table them in the README. Name the slowest and the most expensive step, and one thing that would reduce it.

**Suggested commit messages:** `feat: trace the RAG flow with LangSmith`, `docs: latency and cost per step`

## Decisions

Fill this table in the README once the code is written. Starting questions:

| Question | Decision |
| --- | --- |
| Why exact match for most fields? | The value is either right or wrong, so no judge is needed and the result is free and repeatable. |
| Why a judge only for `purpose`? | It is the one free-text field. A judge costs a call per case. |
| Why a Gemini judge? | DeepEval's default is a paid OpenAI model. The same free key is enough. |
| Why the Day 7 samples as the test set? | They already hold the edge cases, with expected values written before any run. |
| Why copy Day 7 and not import it? | The CI demo worsens the prompt, which must not touch the Day 7 submission. The cost is two copies that can drift. |
| Why live API calls in CI? | A saved output cannot show that a prompt change lowered accuracy. |
| Why a pass-rate threshold, not 100%? | The output is probabilistic. A threshold from the v2 result catches a drop without failing on noise. |
| Why LangSmith? | It is the tool named in the curriculum and has a free tier. |
| Why no result caching? | The suite is 12 calls. Caching would hide the very change the suite is meant to catch. |

## Final step: README, write-up and verification

Write both READMEs: how to run, the decisions table, the results tables, calls made. Create the day file skeleton `part-1/day-09-evals-observability-llmops.md` with links only. The explanation of why LLM features need evals, the Key learnings, the reflection (what I would refuse to ship without an eval) and the AI use section are the user's own words. Add the Day 9 row to the root `README.md`.

**Before finishing, verify each success criterion**

| Criterion | Where it shows |
| --- | --- |
| Explains why LLM features need evals | The user's section in the day file |
| Defines success criteria and a test set | `criteria.md` and `cases.json`, written before the first run |
| Writes LLM tests with DeepEval | `judge.py` and the `GEval` test, with the saved scores |
| Traces calls and reads latency and cost | The Step 5 tables from the LangSmith run |
| Versions and tests prompt changes | `prompts.py` in git, and the v1 vs v2 results from the same suite |
| Runs evals in CI | `evals.yml`, the red and green runs, and the branch protection rule |

Finally, confirm `git status` shows no `.env` and `git diff` contains no key, then suggest the commit message `docs: README and notes`. The user commits.

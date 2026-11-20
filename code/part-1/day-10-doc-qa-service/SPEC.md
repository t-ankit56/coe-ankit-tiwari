# Capstone, A Document Question Answering Service: Build Spec for Claude Code

Build a small Python service that ingests a set of PDF documents into pgvector and answers questions with the source chunks for each answer. Build it test-first and keep the prompts under version control. Add an eval suite for answer quality and run it with the tests in CI through a pull request. Add tracing and report the cost per question.

Project folder: `code/part-1/day-10-doc-qa-service/`. The CI workflow is `.github/workflows/day-10.yml` at the repo root.

Libraries do each step (LangChain), so our own code is small and easy to explain.

## Instructions for Claude Code

1. **Plan mode before every step.** Name the files and the API calls. Do nothing until the user approves.
2. **Never commit.** The user commits. After each step, give a suggested commit message and wait. No Claude attribution.
3. **Test first, one test at a time, in ZOMBIES order** (Step 2 lists the tests): `test:` (red), then `feat:` (green), then `refactor:`.
4. **Minimal API calls.** Name every call and show the exact prompt first. No retries. Save every output under `results/`.
5. **Never print or commit a key.** Keys live in an untracked `.env`, and only `.env.example` is committed. In CI they are repository secrets.
6. **Never invent data.** Expected answers are written from the PDFs before any run.
7. **Use the library, do not rewrite it.** Confirm each class against its current docs and pin the versions.
8. **`NOTES.md`:** one line whenever a result changes a decision.
9. **Presentation notes, key learnings, the reflection and the AI use section are the user's.**

## Models and tools

- Gemini free tier: `gemini-3.1-flash-lite` (temperature 0) and `gemini-embedding-001` (768 dimensions), both pinned.
- Postgres with pgvector, database `day10`.
- Tracing: LangSmith, switched on with environment variables.

| Step | Library |
| --- | --- |
| Read PDFs (keeps `source` and `page`) | `PyPDFLoader` |
| Split | `RecursiveCharacterTextSplitter` |
| Embed | `GoogleGenerativeAIEmbeddings` |
| Store and search | `PGVector` (`langchain-postgres`) |
| Prompt | `ChatPromptTemplate` |
| Generate | `ChatGoogleGenerativeAI` (`usage_metadata` gives the tokens) |
| Tests | `pytest`, `InMemoryVectorStore`, `DeterministicFakeEmbedding`, `GenericFakeChatModel` |
| Eval judge | DeepEval `GEval`, with Gemini as the judge model |

## Design

```
ingest(pdf_dir, store) -> int                  # chunks stored
answer(question, store, llm, prompt) -> dict   # {answer, sources, cost}
```

- `service.py`: `ingest`, `answer`, and a `__main__` with `ingest` and `ask` subcommands. Each source is the document, page and chunk text.
- CLI: `python service.py ingest [path] [--collection NAME]` and `python service.py ask "question" [--collection NAME]`. `path` defaults to `docs/` and the collection defaults to `docs`. To use your own PDFs, paste them into `docs/`, run `ingest`, then `ask`.
- **Ingest rebuilds the collection.** For `ingest`, the CLI opens `PGVector` with `pre_delete_collection=True`, so each run empties the collection and embeds every PDF in the folder again. The collection always matches the folder: added PDFs appear and removed ones disappear. The cost is re-embedding every PDF on each ingest, which is fine for a few PDFs. Incremental ingest is out of scope. `ask` opens the store without that flag so it never deletes anything.
- `prompts.py`: `V1` (bare) and `V2` (cite chunks as `[n]`, and say "I don't know" when the answer is not in the context). `PROMPT_VERSION` picks one and defaults to `v2`.
- `cost.py`: tokens from `usage_metadata` multiplied by the published price per million tokens. The free tier charges nothing, so the cost is notional.
- Tests pass in the in-memory store and the fake models, so they run offline with no database.

## Eval suite

The evals use their own fixed PDF in `evals/docs/`, ingested into the `evals` collection, so changing `docs/` never breaks them. `evals/cases.json` holds 4 cases written from that PDF: 3 facts and 1 question it does not answer. Each case is `{id, question, expected_source, expected_fact}`, with `expected_source` set to `null` for the unanswerable ones.

| Check | How | Passes when |
| --- | --- | --- |
| Source | Code | The expected PDF is among the retrieved chunks. |
| Citation | Code | The answer has a `[n]` that points to a retrieved chunk. |
| Fact | DeepEval `GEval` judge | The answer states the expected fact. The wording may differ. |
| Unanswerable | The same `GEval` judge | The answer says the documents do not contain the answer. The wording may differ. |

A substring match fails correct answers that are worded differently, so a judge does Fact and Unanswerable.

- `evals/judge.py`: one `GEval` correctness metric (DeepEval) on `input`, `actual_output` and `expected_output`. For the unanswerable cases, `expected_output` is "says the answer is not in the documents". The `evaluation_steps` are written out so `GEval` does not spend a call generating them. Gemini (`gemini-3.1-flash-lite`, temperature 0) is the judge model, set up as in Day 9's `judge.py`. Threshold 0.7.
- Each case is one judge call. The judge's score and reason are saved in `results/` next to the answer.
- `REUSE_SAVED=1` judges the saved answers without calling `answer()` again.

The run passes when the share of passing cases is at or above `PASS_RATE`, which is set from the v2 result (one case below it, because 4 cases make 1.0 too strict for CI). Each case is its own test; a failing case is marked `xfail` with the failed checks and the judge's reason, so it shows in the report but only the pass rate can fail the run.

## CI

`.github/workflows/day-10.yml` runs on `pull_request` and on `workflow_dispatch`, and has one job with a `pgvector/pgvector:pg17` service. It installs the requirements, runs `pytest tests`, ingests `evals/docs/` into the `evals` collection, then runs `pytest evals` with `GEMINI_API_KEY` from the secrets. The judge runs in CI because it is the Fact gate. One run makes 7 ingest embedding requests (one per chunk), 4 query embeddings, 4 generations and 4 judge calls, and the README records this. The pull request run is the evidence. `workflow_dispatch` is a manual fallback: if a run fails on a free-tier limit, it can be started again from the Actions tab (or with `gh workflow run day-10.yml --ref <branch>`) without pushing a commit. GitHub only offers this once the workflow is on `main`. Until then, a failed pull request run is re-run with Re-run jobs. No push trigger, so the run count stays low. A `paths` filter limits it to changes in this project or the workflow. `cancel-in-progress: false`, because a cancelled run wastes the calls it has made. Tracing is off in CI, so no LangSmith secret is needed. The Day 9 branch is not merged into `main`, so the pull request targets it, which keeps the diff to Day 10.

## Folder layout

```
code/part-1/day-10-doc-qa-service/
  SPEC.md  README.md  NOTES.md
  requirements.txt  pyproject.toml  .env.example
  docs/                 # your PDFs: paste any here, then ingest
  prompts.py  service.py  cost.py
  tests/                # unit tests
  tests/fixtures/       # one small PDF for the ingest test
  evals/docs/           # the 2-page eval PDF (cases.json is written against it)
  evals/cases.json  evals/judge.py  evals/test_answers.py
  results/              # saved v1 and v2 runs
```

## Step 0: Setup

No API calls.

1. Confirm the LangChain classes and DeepEval's `GEval` (with a Gemini judge model) against their current docs. Also confirm whether `GenericFakeChatModel` keeps `usage_metadata` on the messages it returns (test 16 needs it). If it does not, use a small fake chat model in `tests/support/`.
2. Create the `venv/`, install, freeze `requirements.txt`, and add `pyproject.toml` (pytest `pythonpath = ["."]`).
3. Create the `day10` database with the `vector` extension. Write `.env.example` (`GEMINI_API_KEY`, `DATABASE_URL`, `LANGSMITH_API_KEY`, `LANGSMITH_TRACING`).

**Suggested commit message:** `chore: Day 10 setup`

## Step 1: PDFs and eval cases

No API calls and no code.

1. The eval PDF is pages 1–2 of NCERT Class 10 Science, Chapter 10 (The Human Eye), the same physics as ICSE Class 10. It started as chapters 9 to 11, but ingesting them (172 chunks) hit a 429: the free tier counts each embedded chunk as one request, 100 per minute. The 2 pages make 7 chunks. They are committed as `evals/docs/jesc110-p1-2.pdf`, so the evals and CI run on the exact pages the cases were written from.
2. Read them and write `evals/cases.json`.
3. Add one small text-based PDF to `tests/fixtures/` for the unit tests. `docs/` starts empty with a `.gitkeep`.

**Suggested commit message:** `docs: source PDFs and eval cases`

## Step 2: Test-first cycles

No API calls.

Tests are written in ZOMBIES order: **Z**ero, **O**ne, **M**any, **B**oundaries, **I**nterfaces, **E**xceptions, **S**imple. Each line is one red-green-refactor cycle. A letter that does not fit a unit is skipped rather than forced.

**`cost`** (`tests/test_cost.py`)

| # | Letter | Test |
| --- | --- | --- |
| 1 | Z | Zero input and zero output tokens cost 0. |
| 2 | O | One reply costs input tokens × input price + output tokens × output price, per million. |
| 3 | B | A reply with no `usage_metadata` costs 0 instead of raising an error. |

**`prompts`** (`tests/test_prompts.py`)

| # | Letter | Test |
| --- | --- | --- |
| 4 | S | With no `PROMPT_VERSION`, v2 is picked. |
| 5 | O | `PROMPT_VERSION=v1` picks v1. |
| 6 | I | Both templates take `context` and `question`. |
| 7 | E | An unknown version raises `ValueError`. |

**`ingest`** (`tests/test_ingest.py`, in-memory store, fake embeddings)

| # | Letter | Test |
| --- | --- | --- |
| 8 | Z | An empty folder stores 0 chunks and returns 0. |
| 9 | O | The fixture PDF is stored as chunks that keep `source` and `page`. The return value equals the number stored. |
| 10 | M | Two PDFs in the folder (the fixture copied under two names in `tmp_path`) give chunks from both. |
| 11 | B | Files that are not PDFs in the folder are ignored. |
| 12 | E | A folder that does not exist raises `FileNotFoundError`. |

**`answer`** (`tests/test_answer.py`, in-memory store, fake embeddings, `GenericFakeChatModel`)

| # | Letter | Test |
| --- | --- | --- |
| 13 | Z | An empty store returns "I don't know", no sources and cost 0, without calling the model. |
| 14 | O | With one stored chunk, it returns `{answer, sources, cost}`. The source has document, page and text. |
| 15 | M | With several chunks, the sources are numbered `[1]..[n]` in the context in retrieval order, so citations map back to them. |
| 16 | I | The cost comes from the reply's `usage_metadata` through `cost.py`. |
| 17 | E | A blank question raises `ValueError` without calling the model. |

Tests 13 and 17 save a model call when there is nothing to answer.

The rebuild is the library's `pre_delete_collection` flag, so it gets no unit test. Check it by hand after Step 3: ingest `docs/` twice and confirm the chunk count in the collection stays the same. Then add a PDF, ingest again, and confirm `ask` can answer from both PDFs.

**Suggested commit messages:** one `test:`, `feat:`, `refactor:` per cycle

## Step 3: Evals and tracing

1. Write `evals/judge.py` (the `GEval` metric) and `evals/test_answers.py`: one test per case, plus a pass-rate test against `PASS_RATE`. Show the judge's criteria and `evaluation_steps` before any call.
2. **Named API calls:** 7 embedding requests to ingest (one per chunk), then for v1 and for v2, 4 query embeddings, 4 generations and 4 judge calls each (15 embedding requests and 16 chat calls in all). A 5-second pause before every chat call keeps a run under the free-tier 15 requests per minute (Day 9 hit 429 at 2 seconds). Tracing is on. Save the answers, sources, judge scores and reasons to `results/`.
3. Set `PASS_RATE` from v2. Keep one real failure for the presentation.

**Suggested commit messages:** `test: eval suite for answer quality`, `docs: v1 and v2 eval results`

## Step 4: CI through a pull request

1. Write `day-10.yml` with `pull_request` and `workflow_dispatch` triggers.
2. The user adds the `GEMINI_API_KEY` secret, pushes the branch and opens a pull request. Link the green run in the README.

**Suggested commit message:** `ci: run Day 10 tests and evals on pull requests`

## Step 5: README and day file

1. README: how to run, v1 and v2 pass rates, a cost per question table from the v2 run with the price source and date, a LangSmith trace link, and the CI run link.
2. Day file `part-1/day-10-capstone-doc-qa.md` with links only. Add the Day 10 row to the root `README.md`.

**Suggested commit message:** `docs: Day 10 README and write-up`

| Criterion | Evidence |
| --- | --- |
| End-to-end QA service over PDFs | `service.py`, `results/` with answers and sources |
| Test-first with versioned prompts | `git log` (`test:`, `feat:`, `refactor:`), `prompts.py`, v1 and v2 results |
| Tests and evals in CI through a pull request | `day-10.yml`, the pull request run |
| Reports cost per question | The README cost table |
| Presents design and eval results with an honest failure | The user's presentation, with the failure from Step 3 |
| Comprehensive reflection | The user's section in the day file |

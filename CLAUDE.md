# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Daily submissions for the Incubyte COE (track Python-TS-AI, Part 1). Each day is a write-up plus one or more small, independent projects. There is no root build, no shared package and no root test command: every project under `code/part-1/` is self-contained and is run from its own folder. `erp_leave_module/` is a larger app with its own `CLAUDE.md`. Read that file before touching it, because its rules differ from the ones below (for example its `red:`/`green:` commit messages).

## Layout

- `part-1/day-NN-<topic>.md`: the day's write-up. It holds no source code, only links to the code and README. Key learnings, reflection and the AI use section are the author's own words, so do not draft them.
- `code/part-1/day-NN-<project>/`: one project per criterion. Do not merge two criteria into one project.
- `README.md` (root): an index with one row per day. Add a row when a day is finished.
- Day 4 (`day-04-*`) is SQL/Postgres exercises: a README and a `seed.sql`, no runnable code.
- Days 7 to 9 are Python projects that call the Gemini API (see "LLM days" below).
- `.github/workflows/evals.yml` runs the Day 9 extraction evals on every push and pull request. No other project is in CI.

## Commands

Python projects (Days 1 to 3). Each has its own `venv/` and `requirements.txt`; pytest is configured in the project's `pyproject.toml` (`pythonpath = ["src"]` for the service projects, `["."]` for the Day 1 setup and Day 3 context manager).

```
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
pytest                                   # all tests in the project
pytest tests/test_service.py::test_name -x   # one test, stop at first failure
```

TypeScript projects (Days 5 and 6). Dependencies live in the project's `node_modules`, so nothing is activated.

```
npm install
npm test                                 # vitest run
npm run typecheck                        # tsc --noEmit
npx vitest run tests/api/user-api.test.ts -t "rejects"   # one file or one test name (Day 6 paths)
npm run check                            # Day 6 only: typecheck then tests
npm run build                            # Day 6 only: emits src/ to dist/ via tsconfig.build.json
```

## LLM days (Days 7 to 9)

Python projects like Days 1 to 3 (own `venv/`, `requirements.txt`, `SPEC.md`, `NOTES.md`), but they call the Gemini API (`gemini-3.1-flash-lite`, pinned, temperature 0). Each needs a git-ignored `.env`: copy `.env.example` and add `GEMINI_API_KEY`. Day 8 and Day 9 tracing also need `DATABASE_URL` (Postgres with pgvector, database `day8`), and Day 9 tracing needs a LangSmith key.

- `day-07-llm-extraction`: `extract(source)` (email text or PDF path) returns a Pydantic `Extraction`, with every field Optional. Prompt versions v1 and v2 live in `prompts.py`. No tests.
- `day-08-rag-pgvector`: `rag.py` has `ingest`, `ask` and `compare.py` subcommands. Hand-checked, no tests.
- `day-09-extraction-evals`: a copy of the Day 7 `extract()` plus a pytest eval suite. `cases.json` holds the 12 cases and `criteria.md` the pass rules. `tests/test_matching.py` runs offline. `tests/test_extraction.py` makes 12 live calls and gates on `PASS_RATE`. A DeepEval `GEval` judge (`judge.py`, Gemini-backed) scores `purpose`. Results are saved to `results/`.
- `day-09-rag-tracing`: a copy of the Day 8 RAG flow with LangSmith spans. It reads the `day8` database, so ingest Day 8 first.

```
PROMPT_VERSION=v2 pytest tests/test_extraction.py             # live, v1 or v2
REUSE_SAVED=1 PROMPT_VERSION=v2 pytest tests/test_extraction.py::test_purpose_score   # judge saved outputs, no extract() calls
pytest tests/test_matching.py                                 # no API calls
```

- Day 9 projects are deliberate copies of Day 7 and Day 8 code so the earlier submissions stay untouched. Do not "deduplicate" them.
- Live calls are limited by the free tier: no retries, a 2-second pause between calls, and the call count is recorded in the README. Do not run live tests or the tracing script unless asked. Prefer `REUSE_SAVED=1` and the saved `results/*.json`.
- READMEs are filled from saved results, and the numbers in them come from real runs. Do not edit them by hand.

## How the TypeScript days are built

Both TypeScript days follow the same process, and the process matters as much as the code (it is assessed):

- `SPEC.md` is written first and is the source of truth: ground rules, scope, design, the tests in ZOMBIES order, and one section per red-green-refactor cycle. Read it before changing the project.
- Cycles are strictly test-first, one test at a time. Commit order is `test:` then `feat:` then `refactor:` (also `chore:` and `docs:`), one commit per step, using Conventional Commits.
- `NOTES.md` gets one line whenever a test changes the design. The README summarises the decisions.
- Code is `strict` TypeScript with no `any`. Relative imports use the `.js` extension.
- `npm test` does not type-check. `expectTypeOf` assertions (Day 5) only fail under `npm run typecheck`, so run both.

The two days differ on purpose:

- Day 5 (`day-05-typescript-notification-service`): flat `src/`, a class-based service, and failures returned as a generic `Result<T>`.
- Day 6 (`day-06-typescript-user-api`): `src/` split by role (`models/`, `guards/`, `api/`, with `index.ts` as the public entry) and `tests/` mirroring it, with helpers in `tests/support/`. External data is typed `unknown` and only becomes a `User` through the `isUser` guard. Failures reject the promise instead of returning a `Result`. The fetch function is passed in as a parameter, so tests use a hand-written `fakeFetch` and never touch the network.
- Day 6 uses TypeScript 7, which needs `rootDir` set explicitly. That is why `tsconfig.build.json` exists: `tsconfig.json` includes `tests` for type-checking, and the build must emit only `src`.

## Conventions

- Work identity for commits is the author's Incubyte email (set through `includeIf` in the global git config). Do not add a `Co-Authored-By: Claude` trailer or any other Claude attribution to commits.
- Only commit when asked.
- `.gitignore` excludes `venv/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.idea/`, `.claude/` and `tasks.json`. `node_modules/` and `dist` are ignored inside each TypeScript project's own `.gitignore`.
- Study guides (such as `day-05-typescript-guide.pdf`) and the submission guidelines live outside the repo, in the parent `~/incubyte/` directory.

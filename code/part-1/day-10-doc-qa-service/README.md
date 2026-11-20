# Document question answering service

A small Python service that ingests PDFs into pgvector and answers questions from them. Each answer comes with its numbered source chunks (document, page and text) and a notional cost. It was built test-first from [SPEC.md](SPEC.md), with versioned prompts, an eval suite judged by DeepEval that runs in CI on pull requests, and LangSmith tracing. Design changes made along the way are in [NOTES.md](NOTES.md).

## How to run

```
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cp .env.example .env          # add GEMINI_API_KEY (and LANGSMITH_API_KEY for tracing)
createdb day10 && psql -d day10 -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Your own PDFs:** put them in `docs/`, then:

```
python service.py ingest                      # rebuilds the "docs" collection from docs/
python service.py ask "What is the near point of the eye?"
```

`ingest` empties the collection and embeds every PDF in the folder again, so the collection always matches the folder. Each chunk is one embedding request, and the free tier allows 100 a minute, so keep the PDFs small. Both commands take `--collection NAME`, and `ingest` also takes a folder path.

**Tests and evals:**

```
pytest                                          # 18 offline unit tests, no API calls
python service.py ingest evals/docs --collection evals
PROMPT_VERSION=v2 pytest -rxX evals             # live: 4 cases, judged by DeepEval
```

## Design

| File | What it does |
| --- | --- |
| [service.py](service.py) | `ingest(pdf_dir, store)`: `PyPDFLoader` → `RecursiveCharacterTextSplitter` (1000 characters, 150 overlap) → the vector store. `source` is the file name. `answer(question, store, llm, prompt, k=4)`: retrieve, number the chunks `[1]..[n]`, call the model, return `{answer, sources, cost}`. Plus the `ingest` and `ask` CLI. |
| [prompts.py](prompts.py) | `V1` is bare. `V2` answers only from the numbered chunks, cites them as `[n]` and says "I don't know" otherwise. `PROMPT_VERSION` picks one and defaults to v2. |
| [cost.py](cost.py) | Tokens from `usage_metadata` × the published price per million tokens. |

- **Libraries:** LangChain does each step (`GoogleGenerativeAIEmbeddings`, `PGVector`, `ChatPromptTemplate`, `ChatGoogleGenerativeAI`).
- **Models:** `gemini-3.1-flash-lite` (temperature 0, no retries) and `gemini-embedding-001` (768 dimensions).
- **Separate eval corpus:** the evals use their own PDF and collection (`evals/docs/`, collection `evals`). Changing `docs/` never breaks them.
- **Eval PDF:** [evals/docs/jesc110-p1-2.pdf](evals/docs/jesc110-p1-2.pdf) is pages 1–2 of NCERT Class 10 Science, Chapter 10, committed so the evals and CI run on the exact pages the cases were written from.

## Tests

18 offline tests, using LangChain's in-memory store, fake embeddings and a fake chat model. The first 17 were written one at a time in ZOMBIES order (the table is in [SPEC.md](SPEC.md#step-2-test-first-cycles)), with `test:` → `feat:` → `refactor:` commits.

- **Passed when written:** tests 6, 10 and 11. Test 10 passed because the green step for test 9 already looped over every PDF. See [NOTES.md](NOTES.md).
- **Test 18:** added after the first live run. Gemini 3 replies with a list of content blocks, not a string, which no fake-model test had covered.

## Eval results

**Corpus:** pages 1–2 of NCERT Class 10 Science, Chapter 10 ("The Human Eye"), which make 7 chunks. It started as chapters 9 to 11 (172 chunks), but ingesting them hit a 429: the free tier counts every embedded chunk as one request, 100 a minute.

**Cases:** [evals/cases.json](evals/cases.json) has 3 facts and 1 question the 2 pages do not answer. The expected answers were written from the PDF text before any run.

**Checks:**

| Check | How |
| --- | --- |
| Source | The expected PDF is among the retrieved chunks (code). |
| Citation | Every `[n]` points to a retrieved chunk (code). |
| Fact / Unanswerable | A DeepEval `GEval` judge with Gemini and written-out steps, threshold 0.7 ([evals/judge.py](evals/judge.py)). |

Each case is its own test. A failing case is `xfail` with its reason, and only the pass rate can fail the run.

| Case | v1 (bare prompt) | v2 |
| --- | --- | --- |
| eye-01: what controls the pupil | ✗ no citation (fact right, judge 1.0) | ✓ |
| eye-02: near point | ✗ no citation (fact right, judge 1.0) | ✓ |
| eye-03: cataract | ✗ no citation (fact right, judge 1.0) | ✓ |
| none-01: lens that corrects myopia | ✗ answered from outside knowledge (judge 0.2) | ✓ "I don't know." |
| **Pass rate** | **0/4** | **4/4** |

Full answers, sources, judge scores and reasons: [results/v1.json](results/v1.json) and [results/v2.json](results/v2.json).

**The honest failure (v1, none-01):** page 1 names myopia but not its correction, which is on page 2. v1 noticed that and answered anyway:

> Based on the provided text, it is mentioned that refractive defects of vision "can be corrected by the use of suitable spherical lenses," but the specific type of lens for myopia is not explicitly named in the provided excerpts. However, in standard physics, **concave lenses** are used to correct myopia (near-sightedness).

The judge scored it 0.2 because the answer came from outside the documents. v2's rule to answer only from the context turned this into "I don't know."

**`PASS_RATE` = 0.75:** one case below v2's result of 1.0. With 4 cases, each case moves the rate by 25 points, so 1.0 would fail CI on a single wobble. A drop back to v1 behaviour (0/4) still fails clearly. With this few cases the number is coarse, so the per-case table matters more.

## Cost per question

From the v2 run: tokens from each reply's `usage_metadata` × $0.25 per million input tokens and $1.50 per million output tokens. That is `gemini-3.1-flash-lite`, standard tier, from the [Gemini API pricing page](https://ai.google.dev/gemini-api/docs/pricing), checked 2026-11-20.

| Question | Cost (USD) |
| --- | --- |
| eye-01: what controls the pupil | 0.000243 |
| eye-02: near point | 0.000248 |
| eye-03: cataract | 0.000289 |
| none-01: lens that corrects myopia | 0.000192 |
| **Mean** | **0.000243** |

- **Notional:** the free tier charges nothing, so these costs are what the calls would cost on the paid tier.
- **Generation only:** the query embedding returns no token count, so it is not included.

## Tracing

- **What is traced:** `answer()` has a `@traceable` decorator, so each question is one LangSmith run, with the prompt → model span and its token usage inside.
- **What is recorded:** only the question and `k`. Recording every input serialised the fake model in the unit tests and broke them, see [NOTES.md](NOTES.md).
- **The runs:** the local v1 and v2 runs are in the [LangSmith project](https://smith.langchain.com/o/88d03ba2-fc2f-4e7d-8d2a-bf37830b05b4/a/day-10-doc-qa-service/projects/p/392e4c92-de6d-4b6c-b722-8cbbb4a094dd?runview=traces). The link needs access to the LangSmith organisation.
- **CI:** tracing is off in CI.

## CI

[.github/workflows/day-10.yml](../../../.github/workflows/day-10.yml) runs on pull requests that touch this project. Steps:

1. Starts a `pgvector/pgvector:pg17` service.
2. Installs `requirements.txt` on Python 3.14.
3. Runs the 18 unit tests.
4. Downloads the eval PDF.
5. Ingests it.
6. Runs the eval suite with prompt v2, gated on `PASS_RATE`.

Each run makes 11 embedding requests and 8 chat calls (4 answers and 4 judge calls). `GEMINI_API_KEY` comes from the repository secrets.

**Green run on the pull request:** [run 44705732112](https://github.com/t-ankit56/coe-ankit-tiwari/actions/runs/44705732112).

**Re-running:** the workflow also has `workflow_dispatch`, but GitHub only shows the Run workflow button once the workflow is on `main`. Until then, re-run a failed pull request run with Re-run jobs.

## Calls made (local)

| What | Embedding requests | Chat calls |
| --- | --- | --- |
| Ingest of chapters 9 to 11, hit a 429 | ~100 | 0 |
| Ingest of the 2-page excerpt | 7 | 0 |
| First v1 run, crashed on content blocks before judging | 4 | 4 |
| v1 run | 4 | 8 |
| v2 run | 4 | 8 |
| **Total** | **~119** | **20** |

The first row is approximate: the 429 response does not say how many requests got through. The CI run adds 11 embedding requests and 8 chat calls.

## Not done

- **The hand check of the CLI on `docs/`:** ingest twice and see the same chunk count, then add a PDF, ingest again and `ask`. It costs embedding requests on your own PDFs, so it was left for a manual run.
- **A public trace link:** the LangSmith link above needs organisation access.

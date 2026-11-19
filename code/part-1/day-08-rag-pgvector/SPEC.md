# Embeddings, RAG and pgvector in Python: Build Spec for Claude Code

Build a small retrieval-augmented generation (RAG) flow in Python: split a few documents into chunks, embed them with the Gemini API, store them in PostgreSQL with pgvector, retrieve the closest chunks for a question, and answer from those chunks while showing the sources. Then compare two chunk sizes on the same five questions and record which answered better. This is for the Day 8 assessment, so the recorded results and the commit history matter as much as the final code. Testing is manual (no pytest). Automated evals come on Day 9.

## Instructions for Claude Code

**Ground rules**

1. **Always use plan mode.** Before every step, enter plan mode. The plan names what you will write and which calls you will make. Write no files and make no API calls until the user approves the plan.
2. **Never commit.** Do not run `git add`, `git commit` or any other git command that changes state. Read-only commands such as `git status` and `git diff` are fine. The user makes every commit. After each step, give a suggested commit message, then wait.
3. **One step at a time.** Stop after each step, show what changed and the suggested commit message, then wait for the user to say continue. The user wants to understand each step, not just receive the result.
4. **Keep API calls to a minimum.** Free-tier limits could not be confirmed. Every call must be named in the step's plan and approved, and the exact prompt text is shown before it is sent. Never loop over extra inputs, never retry automatically, never re-run to see if the answer changes. Save every output to a file and fill the README from the saved files.
5. **Never print or commit the key.** `GEMINI_API_KEY` is read from `.env` (gitignored). Do not echo it, log it, or put it in the README, `NOTES.md` or the day file. Only `.env.example` with a placeholder is committed.
6. **No tests.** Do not add pytest, a fake client or an eval script. Checking is manual: expected against got, recorded in the README.
7. **Never invent data.** The documents are made up, about a fictional company, with no real names or figures. Expected answers are written from the documents before any run.
8. **Simplest real thing first.** Dependencies are `google-genai`, `psycopg[binary]` and `python-dotenv` only. No LangChain, no LlamaIndex, no ORM, no vector index, no reranking. The set is tiny, so an exact scan is correct and an index would only add approximation.
9. **Keep notes.** Whenever a result changes a decision (chunk size, top-k, prompt wording), append one line to `NOTES.md`. The user will use these for the reflection.
10. **Reflection, explanation and AI use are the user's.** Do not write them in the day file.
11. **Do not build ahead.** Do not write code, documents or database objects for a step until its plan is approved.

## Provider, models and database

- Google Gemini API, free tier, the same key as Day 7.
- Embedding model: `gemini-embedding-001`, with `output_dimensionality=768`. The pgvector column is `vector(768)`, so the two must match. Confirm the model ID against the key's model list and the docs before the first embedding call.
- Embedding task types: `RETRIEVAL_DOCUMENT` for chunks, `RETRIEVAL_QUERY` for questions.
- Answer model: `gemini-3.1-flash-lite`, as on Day 7. Pin model IDs, never `-latest`.
- Database: the local PostgreSQL 18 cluster with the `postgresql-18-pgvector` package (already installed by the user), in a database named `day8`, extension `vector`. Distance is cosine (`<=>`).

## Scope

- Four short made-up markdown documents in `docs/` (about 700 words in total)
- `chunk(text, size)`: split on word boundaries into pieces of at most `size` characters
- `ingest(size)`: chunk, embed and store, replacing the rows for that size
- `retrieve(question, size, k)`: the k closest chunks with their distance
- `answer(question, size)`: answer from the retrieved chunks, citing them, and return the sources
- Five questions with expected answers, run at two chunk sizes, with every output saved
- A command line: `python rag.py ingest --size N` and `python rag.py ask "question" --size N`


## Design

One table holds every chunk, tagged with its chunk size, so two sizes can sit side by side and be compared on the same data.

```sql
create table chunks (
  id          serial primary key,
  chunk_size  int  not null,
  source      text not null,      -- file name
  position    int  not null,
  content     text not null,
  embedding   vector(768) not null
);
```

| Piece | Job |
| --- | --- |
| `chunk` | Pure function. Words are packed up to `size` characters. |
| `embed` | One call per batch of up to 100 texts, with the given task type. Returns the vectors. |
| `ingest` | Reads every file in `docs/`, chunks, embeds as `RETRIEVAL_DOCUMENT`, deletes the rows for this size, inserts the new ones. |
| `retrieve` | Embeds the question as `RETRIEVAL_QUERY`, then `order by embedding <=> query limit k` for the chosen size. |
| `answer` | Builds a numbered context from the retrieved chunks, asks the model to answer only from it, cite like `[1]`, and say it does not know otherwise. Returns the answer and the sources. |
| `show` | Prints the answer and then every source chunk (file, distance, text). Showing the sources is part of the output, not an option. |

The answer prompt (shown to the user for approval before it is sent): a system instruction that says to use only the numbered context, cite the chunks used, and say "I do not know" when the context lacks the answer; temperature 0.0; `max_output_tokens` 400.

Retrieval uses `k = 3`. It is a constant to be changed only if the results show a reason, and the reason goes in `NOTES.md`.

## Folder layout

```
code/part-1/day-08-rag-pgvector/
  requirements.txt
  .env.example        # GEMINI_API_KEY placeholder and DATABASE_URL; .env is gitignored
  README.md
  NOTES.md
  SPEC.md
  rag.py              # constants, chunk, embed, ingest, retrieve, answer, command line
  compare.py          # runs the five questions at both sizes and saves the outputs
  docs/               # four made-up markdown documents
  questions.md        # the five questions and their expected answers
  results/            # saved outputs per chunk size
```

Python files are flat because the project is small. The `venv/` folder and `.env` are already gitignored at the repo root.

## Step 0: Project setup

Do this first. No API calls yet.

1. Create the `venv/`, activate it, and install `google-genai`, `psycopg[binary]` and `python-dotenv`. Freeze to `requirements.txt`.
2. Create the `day8` database and run `create extension vector`. Check the version with `select extversion from pg_extension where extname = 'vector'`.
3. Copy the Gemini key into this project's untracked `.env`, add `DATABASE_URL=dbname=day8`, and write `.env.example` with placeholders. Confirm `.env` is ignored with `git check-ignore`.
4. Create empty `NOTES.md` and `README.md`.
5. Check the imports and the connection: `python -c "import google.genai, psycopg"` and `psql -d day8 -c "select 1"`.

**Suggested commit message:** `chore: Day 8 project setup with requirements and env example`

## Step 1: documents, questions and expected answers

No API calls and no code.

1. Write four made-up markdown documents in `docs/` (a fictional company handbook: leave, remote work, expenses, security). Each is short, with headings and concrete facts (numbers, limits, deadlines).
2. Write `questions.md` with five questions and the expected answer to each, written from the documents before anything is run. Include:
   - four questions answered by a single sentence in one place,
   - one question whose answer is split across two sections of the same document.

**Suggested commit message:** `docs: handbook documents and five questions with expected answers`

## Step 2: chunking

No API calls.

1. `rag.py`: the constants and `chunk(text, size)`.
2. Print the chunks of one document at sizes 300 and 1000 and check them by eye: nothing is lost, no word is cut, no chunk is over `size`.

**Suggested commit message:** `feat: split documents into chunks of a given size`

## Step 3: embed and store in pgvector

1. `embed` and `ingest` in `rag.py`, and the `ingest` command. The table is created if it does not exist.
2. **Named API call:** `embed_content` with `RETRIEVAL_DOCUMENT`, one batched call per ingest. Ingest size 600 once as a trial.
3. Check with SQL: the row count and the vector dimension (`select vector_dims(embedding) from chunks limit 1`).

**Suggested commit message:** `feat: embed chunks with Gemini and store them in pgvector`

## Step 4: retrieve with sources

1. `retrieve` and the `show` helper for retrieval only.
2. **Named API call:** `embed_content` with `RETRIEVAL_QUERY`, one per question. Run the first question at size 600 and look at the three chunks and their distances.
3. Explain in the README, in a sentence or two, what the distance means and why the same chunk can rank first for a differently worded question.

**Suggested commit message:** `feat: retrieve the closest chunks by cosine distance`

## Step 5: answer with sources

1. `answer` and the `ask` command. The user approves the exact prompt text first.
2. **Named API call:** `generate_content`, one call, on the first question at size 600.
3. Confirm that the output shows the answer, the citation and every source chunk.

**Suggested commit message:** `feat: answer questions from retrieved chunks and show sources`

## Step 6: compare two chunk sizes

1. `compare.py`: for sizes 300 and 1000, ingest, then run the five questions through `answer` once each, saving `results/size-<n>.json` and a readable `.txt` with the answers and sources.
2. **Named API calls:** 2 ingest batches, 10 query embeddings, 10 answer calls, once each, with a pause between calls. If the quota is hit, stop and report; do not retry.
3. In the README, add a table of question, expected answer, answer at 300, answer at 1000, and which was better, judged by hand against `questions.md`.
4. Five questions are a small sample, and the README must say so.

**Suggested commit messages:** `feat: compare chunk sizes on the same five questions`, `docs: chunk size results and comparison`

## Decisions

Fill this table in the README once the code is written. Starting questions:

| Question | Decision |
| --- | --- |
| Why Gemini embeddings? | Same free key as Day 7. Anthropic has no embeddings endpoint. |
| Why 768 dimensions? | Smaller column and faster scan, at little cost for a small set. The column and `output_dimensionality` must match. |
| Why two task types? | The model embeds a stored passage and a search query differently, and retrieval works better when they are marked. |
| Why cosine distance? | It compares direction, not length, which suits text embeddings. |
| Why no index? | About twenty rows. An exact scan is correct and an approximate index would only add risk. |
| Why one table with a `chunk_size` column? | Both sizes sit side by side and the comparison runs on the same data. |
| Why chunk on words and not characters? | A word is never cut in half. Sizes are still counted in characters so the two are easy to compare. |
| Why k = 3? | Enough to catch an answer split across neighbours, small enough to keep the prompt short. |
| Why tell the model to say "I do not know"? | Without it the model fills a gap from memory, and the sources shown would not match the answer. |
| Why manual checking and no pytest? | Same as Day 7: the output is probabilistic, and evals come on Day 9. |

## Final step: README, manual check and verification

Write `README.md` with these parts:

1. What it is and how to run it (`pip install -r requirements.txt`, `python rag.py ingest --size 600`, `python rag.py ask "..." --size 600`), with the database setup.
2. How the flow works, in a short diagram or list: chunk, embed, store, retrieve, answer.
3. The decisions table, the five questions, and the comparison table with the sources behind each answer.
4. The models used, the number of API calls made, and the limits met.

The explanation of embeddings and semantic search against keyword search, the Key learnings, the reflection (when retrieval is right and when a longer prompt is enough) and the AI use section go in `part-1/day-08-embeddings-rag-pgvector.md`, in the user's own words. Add the Day 8 row to the root `README.md`.

**Before finishing, verify each success criterion**

| Criterion | Where it shows |
| --- | --- |
| Explains embeddings and semantic search | The user's section in the day file, with the Step 4 distance note in the README as evidence |
| Builds a basic RAG flow | `answer()` in `rag.py` and a saved run of `ask` |
| Stores and queries embeddings with pgvector | The `chunks` table, the `<=>` query in `retrieve()`, and the SQL checks from Step 3 |
| Shows sources for each answer | `show()` prints every source chunk, and every saved result includes them |
| Compares chunking choices with evidence | The Step 6 table, built from `results/size-300` and `results/size-1000` on the same five questions |

Finally, confirm `git status` shows no `.env` and `git diff` contains no key, then suggest the commit message `docs: README and notes`. The user commits.

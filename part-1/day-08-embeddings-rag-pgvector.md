# Part 1 · Day 8 — Embeddings, RAG & pgvector

**Date completed:** 2026-11-18 · **Time spent:**

## Success criteria

| Criterion (copied from the planner) | Done? | Evidence (link or section below) |
| --- | --- | --- |
| Explains embeddings and semantic search | Yes | [Key learnings](#key-learnings) · [distance note](../code/part-1/day-08-rag-pgvector/README.md#distance) |
| Builds a basic RAG flow | Yes | [rag.py](../code/part-1/day-08-rag-pgvector/rag.py) · [how the flow works](../code/part-1/day-08-rag-pgvector/README.md#how-the-flow-works) |
| Stores and queries embeddings with pgvector | Yes | [ingest and retrieve in rag.py](../code/part-1/day-08-rag-pgvector/rag.py) · [decisions](../code/part-1/day-08-rag-pgvector/README.md#decisions) |
| Shows sources for each answer | Yes | [saved answers with their source chunks](../code/part-1/day-08-rag-pgvector/results/) |
| Compares chunking choices with evidence | Yes | [chunk size comparison](../code/part-1/day-08-rag-pgvector/README.md#chunk-size-comparison) · [results](../code/part-1/day-08-rag-pgvector/results/) |

## Key learnings

- **Embeddings and semantic search:** an embedding turns a text into a list of numbers (here 768) so that texts with a similar meaning end up close together. Search then compares meaning, not shared words, which is what keyword search matches. pgvector's `<=>` is cosine distance: the smallest distance is the closest chunk. Gemini wants a task type, `RETRIEVAL_DOCUMENT` for stored chunks and `RETRIEVAL_QUERY` for questions.
- **RAG and sources:** the flow is chunk, embed, store, retrieve, answer. The model is told to answer only from the numbered chunks, cite them like `[1]`, and say it does not know otherwise. Every answer prints its source chunks, so each one can be checked against the document.
- **Chunk size:** on five questions both sizes answered everything correctly. Size 300 sent about a third of the text (744 against 1,966 characters) and its closest chunk was nearer every time, but it cut two answers across two chunks and only worked because the top 3 brought both. Five questions over four short documents is too small a test to say that 1000 is safer.
- **Quota:** the Gemini SDK retries a failed request 5 times by default, which would spend the free quota on failures. I set `attempts=1` so a failure stops the run.

## Exercises

### Practice: load documents into pgvector and answer with retrieved context

Spec: [SPEC.md](../code/part-1/day-08-rag-pgvector/SPEC.md) · Code and decisions: [README](../code/part-1/day-08-rag-pgvector/README.md)

Four made-up handbook documents (677 words) are split into chunks, embedded with `gemini-embedding-001` and stored in a `chunks` table with a `vector(768)` column in local PostgreSQL. `python rag.py ask "..."` retrieves the 3 closest chunks and answers from them with `gemini-3.1-flash-lite`.

### Exercise 1: show the source chunks for every answer

`show()` prints the answer and then every retrieved chunk with its file and distance, and each result in [results/](../code/part-1/day-08-rag-pgvector/results/) keeps them. In the first run the right chunk ranked first (distance 0.335) and the other two were close to each other and did not answer the question. See the [distance note](../code/part-1/day-08-rag-pgvector/README.md#distance).

### Exercise 2: compare two chunk sizes on the same five questions

The five questions in [questions.md](../code/part-1/day-08-rag-pgvector/questions.md) were written with expected answers before any run, then run at 300 and 1000 characters (16 and 5 chunks). All ten answers were correct, so neither size answered better. Size 300 used less context and retrieved more precisely, at the risk of splitting a fact. See the [comparison](../code/part-1/day-08-rag-pgvector/README.md#chunk-size-comparison).

## Reflection

For this set a longer prompt would have been enough. All four documents are 677 words, so I could have put them in every prompt and skipped the database, the embeddings and the chunking. At size 1000 the retrieval was already close to that, since a chunk was nearly a whole document. Retrieval is the right answer when the documents are too many or too long to send each time, when sending them all makes every question slow and costly, or when I need to show which part of which document an answer came from. A longer prompt is simpler and cannot miss the right chunk, so I would start with it and move to retrieval only when the documents stop fitting. The test also taught me that the comparison needs harder questions than mine: none of the five broke at 300, so it could not show when a small chunk fails.

## AI use

I used Claude Code (Sonnet 5.5) for this day. It wrote the made-up documents, the five questions and their expected answers, the code, the README and the saved results. I asked for the spec first and approved each step's plan and each batch of API calls before it ran. I also removed extras from the spec (chunk overlap, an extra unanswerable-question check, saved chunk and SQL outputs, an out-of-scope section). An earlier build started before the spec was approved, and I had it thrown away. Claude also drafted the Key learnings, exercise summaries and Reflection from the results of this run. [Edit this paragraph to say what you checked and what you changed.]

## Open questions

- Which question would make size 300 fail, for example a fact split across two chunks with a smaller `k`?
- How would a keyword search compare with the vector search on a question that shares no words with the document?
- Would contextual retrieval (adding a short context to each chunk before embedding) help the split answers? I only read about it.
- Does the Gemini embedding response report token usage? Day 9's tracing and cost per question need it, and I have not checked.

## Changes after review

- 

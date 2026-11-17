# Embeddings, RAG and pgvector

Spec: [SPEC.md](SPEC.md) · Notes: [NOTES.md](NOTES.md)

A small retrieval-augmented generation (RAG) flow over four made-up handbook documents in [docs/](docs/). The documents are split into chunks, embedded with Gemini, stored in PostgreSQL with pgvector, and a question is answered from the closest chunks. Every answer prints the source chunks it was built from. There are no automated tests (evals are Day 9), so the results below were checked by hand.

## How to run

```
sudo apt install postgresql-18-pgvector
psql -d postgres -c "create database day8"
psql -d day8 -c "create extension vector"

python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then put a Gemini API key in .env

python rag.py ingest --size 600
python rag.py ask "How many leave days can I carry over, and when do they expire?" --size 600
python compare.py           # five questions at sizes 300 and 1000, saved in results/
```

## How the flow works

1. `chunk(text, size)` splits a document on word boundaries into pieces of at most `size` characters.
2. `embed(texts, task_type)` turns texts into 768-number vectors with `gemini-embedding-001`. Chunks use `RETRIEVAL_DOCUMENT` and questions use `RETRIEVAL_QUERY`.
3. `ingest(size)` stores each chunk and its vector in the `chunks` table, tagged with its chunk size.
4. `retrieve(question, size)` embeds the question and returns the 3 chunks with the smallest cosine distance (`<=>`).
5. `answer(question, size)` sends those chunks to `gemini-3.1-flash-lite`, asks for an answer that uses only them and cites them like `[1]`, and returns the answer with the sources. `show()` prints both.

## Decisions

| Question | Decision |
| --- | --- |
| Why Gemini embeddings? | Same free key as Day 7. Anthropic has no embeddings endpoint. |
| Why 768 dimensions? | A smaller column and a faster scan, at little cost for a small set. The column and `output_dimensionality` must match. |
| Why two task types? | The model embeds a stored passage and a search query differently, and retrieval works better when they are marked. |
| Why cosine distance? | It compares direction, not length, which suits text embeddings. |
| Why no index? | About twenty rows. An exact scan is correct, and an approximate index would only add risk. |
| Why one table with a `chunk_size` column? | Both sizes sit side by side and the comparison runs on the same data. |
| Why chunk on words and not characters? | A word is never cut in half. Sizes are still counted in characters so the two are easy to compare. |
| Why k = 3? | Enough to catch an answer split across neighbours, small enough to keep the prompt short. |
| Why tell the model to say "I do not know"? | Without it the model fills a gap from memory, and the sources shown would not match the answer. |
| Why `attempts=1` on the client? | The SDK retries failed requests 5 times by default. A retry loop spends the free quota on failures, so a failed call raises an error instead. |
| Why manual checking and no pytest? | The output is probabilistic, and evals come on Day 9. |

## Distance

The `<=>` operator in pgvector is cosine distance. It is 0 when two vectors point the same way and grows the further apart two texts are in meaning, so the smallest distance is the closest chunk. Because it compares the meaning that the embedding captured and not shared words, a question does not have to use the document's wording to find its chunk.

Example, question 1 ("How many leave days can I carry over, and when do they expire?") at chunk size 600, top 3:

| Rank | Source | Distance | Holds the answer? |
| --- | --- | --- | --- |
| 1 | leave-policy.md | 0.335 | Yes ("Up to 5 unused days ... expire on 31 March") |
| 2 | leave-policy.md | 0.396 | No |
| 3 | remote-work.md | 0.404 | No |

The right chunk is clearly closest. Ranks 2 and 3 are close to each other and neither answers the question, so with `k = 3` they are padding, not evidence.

## Chunk size comparison

The same five questions from [questions.md](questions.md), run at two chunk sizes over the four documents (677 words). Each run retrieves the top 3 chunks. Every answer and its source chunks are saved in [results/](results/): `size-300` gives 16 chunks and `size-1000` gives 5. Each answer was judged by hand against the expected answer.

| # | Question | Answer at 300 | Answer at 1000 | Better |
| --- | --- | --- | --- | --- |
| 1 | Leave days carried over, and when they expire | Correct. The two facts sit in two different chunks, both retrieved, cited as [2] and [1]. | Correct. One chunk holds both. | Tie |
| 2 | Medical certificate for one day | Correct | Correct | Tie |
| 3 | Hotel cap in a small city, and where to book | Correct | Correct | Tie |
| 4 | Report a stolen laptop | Correct on "within 1 hour". Leaves out "day or night". | Same | Tie |
| 5 | Remote work in probation, and internet reimbursement | Correct, using two chunks ([3] and [2]). Adds the 3 days a week allowed after probation. | Correct, from one chunk. | Tie |

**Result:** all five answers were correct at both sizes, so on these questions neither size answered better. What differed was what was retrieved:

| | Size 300 | Size 1000 |
| --- | --- | --- |
| Characters sent as context per question (average) | 744 | 1,966 |
| Distance of the closest chunk (range over the five questions) | 0.278 to 0.337 | 0.294 to 0.404 |
| Question 1 and 5 | The answer was spread over two chunks, and top 3 was enough to bring both | One chunk held it |
| Rest of the top 3 | Mostly the right document | Mostly other documents, or a one-sentence leftover chunk |

Size 300 sent about a third of the text and its closest chunk was nearer in all five questions. Its cost is that a fact can be cut across two chunks (question 1 and 5), and it only worked because `k = 3` retrieved the neighbour.

**Limits of this test:** five questions over four short documents is a small sample. At 1000 characters a chunk is nearly a whole document, so retrieval can hardly miss the right one, and none of the five questions broke at 300 either. The test does not show a case where a split fact lost the answer, so it cannot say that 1000 is safer.

## Models, calls and limits

- Models: `gemini-embedding-001` (768 dimensions) and `gemini-3.1-flash-lite`, pinned by name. Database: PostgreSQL 18 with pgvector 0.8.1.
- API calls made by the project as built: 27 (one model-list check and one embedding in the first ingest, one query embedding for the distance example, two for the first answer, and 22 for the comparison). An earlier prototype that was discarded before the spec was approved used about 25 more on the same key.
- Limits met: none. There were no rate-limit or quota errors. The free-tier limits themselves were not confirmed from the documentation.

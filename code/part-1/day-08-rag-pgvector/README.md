# Embeddings, RAG and pgvector

Spec: [SPEC.md](SPEC.md) · Notes: [NOTES.md](NOTES.md)

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

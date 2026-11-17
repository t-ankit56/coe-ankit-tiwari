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

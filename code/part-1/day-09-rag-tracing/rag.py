"""Day 8 RAG flow (chunk, embed, store, retrieve, answer) with LangSmith tracing and a per-step record of latency, tokens and cost."""
import argparse
import os
import time
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree

EMBED_MODEL = "gemini-embedding-001"
GEN_MODEL = "gemini-3.1-flash-lite"
DIMENSIONS = 768
TOP_K = 3
DOCS = Path(__file__).parent / "docs"

# Paid-tier price per million tokens in USD, from the Gemini API pricing page (ai.google.dev/gemini-api/docs/pricing),
# read on 2026-11-18. The free tier charges nothing, so the cost below is notional.
GEN_INPUT_PER_M = 0.25
GEN_OUTPUT_PER_M = 1.50
EMBED_INPUT_PER_M = 0.15

# One entry per traced step of the current question: name, seconds, tokens and cost. trace_run.py reads and clears it.
STEPS: list[dict] = []

load_dotenv(Path(__file__).parent / ".env")


def chunk(text: str, size: int) -> list[str]:
    """Split text into pieces of at most `size` characters, never cutting a word."""
    chunks: list[str] = []
    current = ""
    for word in text.split():
        if current and len(current) + 1 + len(word) > size:
            chunks.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        chunks.append(current)
    return chunks


def client() -> genai.Client:
    # attempts=1 means no automatic retry (the SDK default is 5, which would spend quota on failures)
    options = types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=1))
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=options)


def connect() -> psycopg.Connection:
    return psycopg.connect(os.environ["DATABASE_URL"])


def embed(texts: list[str], task_type: str) -> list[list[float]]:
    """Embed texts with Gemini, at most 100 per call."""
    gemini = client()  # keep a reference: a temporary client closes its connection when collected
    vectors: list[list[float]] = []
    for i in range(0, len(texts), 100):
        response = gemini.models.embed_content(
            model=EMBED_MODEL,
            contents=texts[i : i + 100],
            config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=DIMENSIONS),
        )
        vectors += [e.values for e in response.embeddings]
    return vectors


def literal(vector: list[float]) -> str:
    return "[" + ",".join(str(x) for x in vector) + "]"


def ingest(size: int) -> int:
    """Chunk every file in docs/, embed the chunks and store them, replacing the rows for this size."""
    pieces = [(path.name, c) for path in sorted(DOCS.glob("*.md")) for c in chunk(path.read_text(), size)]
    vectors = embed([c for _, c in pieces], "RETRIEVAL_DOCUMENT")
    with connect() as conn:
        conn.execute(
            f"""create table if not exists chunks (
                id serial primary key, chunk_size int not null, source text not null,
                position int not null, content text not null, embedding vector({DIMENSIONS}) not null)"""
        )
        conn.execute("delete from chunks where chunk_size = %s", (size,))
        for position, ((source, content), vector) in enumerate(zip(pieces, vectors)):
            conn.execute(
                "insert into chunks (chunk_size, source, position, content, embedding) values (%s, %s, %s, %s, %s::vector)",
                (size, source, position, content, literal(vector)),
            )
    return len(pieces)


def record(name: str, seconds: float, input_tokens: int = 0, output_tokens: int = 0, cost: float = 0.0, estimated: bool = False) -> None:
    """Keep the step's numbers locally and attach the token usage and cost to the LangSmith span."""
    STEPS.append({"step": name, "seconds": round(seconds, 3), "input_tokens": input_tokens, "output_tokens": output_tokens,
                  "cost_usd": cost, "tokens_estimated": estimated})
    run = get_current_run_tree()
    if run is not None and (input_tokens or output_tokens):
        run.metadata["usage_metadata"] = {"input_tokens": input_tokens, "output_tokens": output_tokens,
                                          "total_tokens": input_tokens + output_tokens, "total_cost": cost}


@traceable(run_type="embedding", name="embed_query", process_outputs=lambda vector: {"dimensions": len(vector)})
def embed_query(question: str) -> list[float]:
    """Embed the question. The API returns no token count, so tokens are estimated as characters / 4."""
    start = time.perf_counter()
    (vector,) = embed([question], "RETRIEVAL_QUERY")
    tokens = max(1, round(len(question) / 4))
    record("embed_query", time.perf_counter() - start, tokens, 0, tokens * EMBED_INPUT_PER_M / 1e6, estimated=True)
    return vector


@traceable(run_type="retriever", name="vector_search", process_inputs=lambda inputs: {"size": inputs["size"], "k": inputs["k"]})
def vector_search(vector: list[float], size: int, k: int) -> list[dict]:
    """The k chunks of this size closest to the question vector, by cosine distance."""
    start = time.perf_counter()
    with connect() as conn:
        rows = conn.execute(
            """select source, content, embedding <=> %s::vector as distance
               from chunks where chunk_size = %s order by distance limit %s""",
            (literal(vector), size, k),
        ).fetchall()
    record("vector_search", time.perf_counter() - start)
    return [{"source": source, "content": content, "distance": float(distance)} for source, content, distance in rows]


def retrieve(question: str, size: int, k: int = TOP_K) -> list[dict]:
    """The k chunks of this size closest to the question, by cosine distance."""
    return vector_search(embed_query(question), size, k)


def show_sources(sources: list[dict]) -> str:
    return "\n".join(
        f"[{i}] {s['source']} (distance {s['distance']:.3f})\n    {s['content']}" for i, s in enumerate(sources, 1)
    )


SYSTEM = (
    "Answer the question using only the numbered context chunks. Cite the chunks you used like [1]. "
    "If the context does not contain the answer, say you do not know."
)


@traceable(run_type="llm", name="generate_answer")
def generate_answer(question: str, sources: list[dict]) -> str:
    """Ask the model to answer from the numbered chunks."""
    context = "\n\n".join(f"[{i}] ({s['source']}) {s['content']}" for i, s in enumerate(sources, 1))
    gemini = client()
    start = time.perf_counter()
    response = gemini.models.generate_content(
        model=GEN_MODEL,
        contents=f"Context:\n{context}\n\nQuestion: {question}",
        config=types.GenerateContentConfig(system_instruction=SYSTEM, temperature=0.0, max_output_tokens=400),
    )
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count or 0
    output_tokens = (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
    cost = (input_tokens * GEN_INPUT_PER_M + output_tokens * GEN_OUTPUT_PER_M) / 1e6
    record("generate_answer", time.perf_counter() - start, input_tokens, output_tokens, cost)
    return response.text


@traceable(run_type="chain", name="answer")
def answer(question: str, size: int) -> dict:
    """Answer from the retrieved chunks and return the answer together with those chunks."""
    sources = retrieve(question, size)
    return {"question": question, "answer": generate_answer(question, sources), "sources": sources}


def show(result: dict) -> str:
    return f"Q: {result['question']}\nA: {result['answer'].strip()}\n\nSources:\n{show_sources(result['sources'])}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    ingest_parser = sub.add_parser("ingest", help="chunk, embed and store the documents")
    ingest_parser.add_argument("--size", type=int, default=600)
    ask_parser = sub.add_parser("ask", help="answer a question from the stored chunks")
    ask_parser.add_argument("question")
    ask_parser.add_argument("--size", type=int, default=600)
    args = parser.parse_args()
    if args.command == "ingest":
        print(f"stored {ingest(args.size)} chunks of up to {args.size} characters")
    else:
        print(show(answer(args.question, args.size)))

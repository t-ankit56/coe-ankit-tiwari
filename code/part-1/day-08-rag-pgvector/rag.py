"""Basic RAG over a few markdown files: chunk, embed (Gemini), store (pgvector), retrieve, answer."""
import argparse
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from google import genai
from google.genai import types

EMBED_MODEL = "gemini-embedding-001"
GEN_MODEL = "gemini-3.1-flash-lite"
DIMENSIONS = 768
TOP_K = 3
DOCS = Path(__file__).parent / "docs"

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
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    ingest_parser = sub.add_parser("ingest", help="chunk, embed and store the documents")
    ingest_parser.add_argument("--size", type=int, default=600)
    args = parser.parse_args()
    if args.command == "ingest":
        print(f"stored {ingest(args.size)} chunks of up to {args.size} characters")

"""Basic RAG over a few markdown files: chunk, embed (Gemini), store (pgvector), retrieve, answer."""
from pathlib import Path

EMBED_MODEL = "gemini-embedding-001"
GEN_MODEL = "gemini-3.1-flash-lite"
DIMENSIONS = 768
TOP_K = 3
DOCS = Path(__file__).parent / "docs"


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

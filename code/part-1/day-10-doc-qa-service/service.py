"""Document question answering over PDFs: ingest into a vector store, answer with sources."""
import argparse
import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from cost import cost

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


def load_pages(pdf: Path) -> list[Document]:
    """One Document per page, with `source` set to the file name."""
    pages = PyPDFLoader(str(pdf)).load()
    for page in pages:
        page.metadata["source"] = pdf.name
    return pages


def ingest(pdf_dir: str | Path, store: VectorStore) -> int:
    """Split every PDF in `pdf_dir` into chunks, add them to `store`, return the count."""
    folder = Path(pdf_dir)
    if not folder.is_dir():
        raise FileNotFoundError(f"No such folder: {folder}")
    pages = [page for pdf in sorted(folder.glob("*.pdf")) for page in load_pages(pdf)]
    chunks = splitter.split_documents(pages)
    if chunks:
        store.add_documents(chunks)
    return len(chunks)


def answer(question: str, store: VectorStore, llm: Runnable,
           prompt: ChatPromptTemplate, k: int = 4) -> dict:
    """Answer from the top `k` chunks. Returns {answer, sources, cost}.

    Sources are numbered from 1 in retrieval order, matching the [n] labels in the context.
    """
    if not question.strip():
        raise ValueError("Question is blank")
    docs = store.similarity_search(question, k=k)
    if not docs:
        return {"answer": "I don't know", "sources": [], "cost": 0.0}
    sources = [{"n": n, "document": d.metadata["source"],
                "page": d.metadata["page"], "text": d.page_content}
               for n, d in enumerate(docs, start=1)]
    context = "\n\n".join(f"[{s['n']}] {s['text']}" for s in sources)
    reply = (prompt | llm).invoke({"context": context, "question": question})
    return {"answer": reply.content, "sources": sources, "cost": cost(reply.usage_metadata)}


# --- CLI: wiring only, needs the network and Postgres, so it has no unit test ---

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_SIZE = 768
CHAT_MODEL = "gemini-3.1-flash-lite"


def make_store(collection: str, rebuild: bool = False) -> VectorStore:
    """PGVector store. rebuild=True empties the collection first (ingest only, never ask)."""
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_postgres import PGVector

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL, output_dimensionality=EMBEDDING_SIZE)  # no retries by default
    return PGVector(
        embeddings=embeddings,
        connection=os.environ["DATABASE_URL"],
        collection_name=collection,
        embedding_length=EMBEDDING_SIZE,
        pre_delete_collection=rebuild,
    )


def make_llm() -> Runnable:
    from langchain_google_genai import ChatGoogleGenerativeAI

    # max_retries is the total number of attempts, so 1 means no retry.
    return ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0, max_retries=1)


def main(argv: list[str] | None = None) -> None:
    from dotenv import load_dotenv

    from prompts import get_prompt

    load_dotenv(Path(__file__).parent / ".env")
    parser = argparse.ArgumentParser(description="Question answering over PDFs.")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest_cmd = commands.add_parser("ingest", help="rebuild a collection from a folder of PDFs")
    ingest_cmd.add_argument("path", nargs="?", default=Path(__file__).parent / "docs")
    ingest_cmd.add_argument("--collection", default="docs")
    ask_cmd = commands.add_parser("ask", help="answer a question from a collection")
    ask_cmd.add_argument("question")
    ask_cmd.add_argument("--collection", default="docs")
    args = parser.parse_args(argv)

    if args.command == "ingest":
        count = ingest(args.path, make_store(args.collection, rebuild=True))
        print(f"Stored {count} chunks in collection '{args.collection}'.")
    else:
        result = answer(args.question, make_store(args.collection), make_llm(), get_prompt())
        print(result["answer"])
        for s in result["sources"]:
            print(f"  [{s['n']}] {s['document']}, page {s['page']}")
        print(f"Cost: ${result['cost']:.6f} (notional)")


if __name__ == "__main__":
    main()

"""Document question answering over PDFs: ingest into a vector store, answer with sources."""
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

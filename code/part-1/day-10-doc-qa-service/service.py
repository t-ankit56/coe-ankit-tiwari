from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)


def ingest(pdf_dir, store):
    folder = Path(pdf_dir)
    if not folder.is_dir():
        raise FileNotFoundError(f"No such folder: {folder}")
    pages = []
    for pdf in folder.glob("*.pdf"):
        for page in PyPDFLoader(str(pdf)).load():
            page.metadata["source"] = pdf.name
            pages.append(page)
    chunks = splitter.split_documents(pages)
    if chunks:
        store.add_documents(chunks)
    return len(chunks)

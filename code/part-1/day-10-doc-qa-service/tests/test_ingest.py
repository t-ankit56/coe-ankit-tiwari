import shutil
from pathlib import Path

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore

from service import ingest

FIXTURE = Path(__file__).parent / "fixtures" / "dummy.pdf"


@pytest.fixture
def store():
    return InMemoryVectorStore(DeterministicFakeEmbedding(size=768))


def stored_chunks(store):
    return list(store.store.values())


def test_empty_folder_stores_no_chunks(tmp_path, store):
    assert ingest(tmp_path, store) == 0
    assert store.store == {}


def test_one_pdf_is_stored_as_chunks_that_keep_document_and_page(tmp_path, store):
    shutil.copy(FIXTURE, tmp_path / "dummy.pdf")

    assert ingest(tmp_path, store) == 1
    [chunk] = stored_chunks(store)
    assert chunk["metadata"]["source"] == "dummy.pdf"
    assert chunk["metadata"]["page"] == 0
    assert "Dummy PDF file" in chunk["text"]


def test_many_pdfs_give_chunks_from_each(tmp_path, store):
    shutil.copy(FIXTURE, tmp_path / "a.pdf")
    shutil.copy(FIXTURE, tmp_path / "b.pdf")

    assert ingest(tmp_path, store) == 2
    assert {c["metadata"]["source"] for c in stored_chunks(store)} == {"a.pdf", "b.pdf"}

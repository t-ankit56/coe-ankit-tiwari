import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore

from service import ingest


@pytest.fixture
def store():
    return InMemoryVectorStore(DeterministicFakeEmbedding(size=768))


def test_empty_folder_stores_no_chunks(tmp_path, store):
    assert ingest(tmp_path, store) == 0
    assert store.store == {}

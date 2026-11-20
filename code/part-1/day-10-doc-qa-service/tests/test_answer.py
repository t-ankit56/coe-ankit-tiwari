import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.vectorstores import InMemoryVectorStore

from prompts import V2
from service import answer


@pytest.fixture
def store():
    return InMemoryVectorStore(DeterministicFakeEmbedding(size=768))


class Recorder:
    """Stands in for the chat model: records each prompt it gets and replies with a fixed message."""

    def __init__(self, reply="a reply"):
        self.prompts = []
        self.reply = reply
        self.llm = RunnableLambda(self._call)

    def _call(self, prompt_value):
        self.prompts.append(prompt_value.to_string())
        return AIMessage(content=self.reply)


def test_empty_store_answers_i_dont_know_without_calling_the_model(store):
    recorder = Recorder()

    result = answer("What is a dioptre?", store, recorder.llm, V2)

    assert result == {"answer": "I don't know", "sources": [], "cost": 0.0}
    assert recorder.prompts == []


def test_one_chunk_returns_the_answer_with_its_source(store):
    store.add_texts(["The SI unit of power of a lens is dioptre."],
                    metadatas=[{"source": "a.pdf", "page": 0}])
    llm = GenericFakeChatModel(messages=iter([AIMessage(content="Dioptre [1].")]))

    result = answer("What is the unit of power of a lens?", store, llm, V2)

    assert result["answer"] == "Dioptre [1]."
    assert result["sources"] == [{
        "n": 1,
        "document": "a.pdf",
        "page": 0,
        "text": "The SI unit of power of a lens is dioptre.",
    }]

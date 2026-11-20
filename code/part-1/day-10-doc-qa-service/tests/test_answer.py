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


def test_many_chunks_are_numbered_in_retrieval_order_in_sources_and_prompt(store):
    store.add_texts(
        ["Near point is 25 cm.", "Far point is infinity.", "Stars twinkle."],
        metadatas=[{"source": "eye.pdf", "page": p} for p in (1, 2, 7)],
    )
    question = "What is the near point?"
    retrieved = store.similarity_search(question, k=3)
    recorder = Recorder()

    result = answer(question, store, recorder.llm, V2, k=3)

    assert [s["n"] for s in result["sources"]] == [1, 2, 3]
    assert [s["text"] for s in result["sources"]] == [d.page_content for d in retrieved]
    [prompt] = recorder.prompts
    for n, doc in enumerate(retrieved, start=1):
        assert f"[{n}] {doc.page_content}" in prompt


def test_cost_comes_from_the_reply_usage_metadata(store):
    store.add_texts(["1 kW h = 3.6 x 10^6 J."], metadatas=[{"source": "elec.pdf", "page": 20}])
    usage = {"input_tokens": 2000, "output_tokens": 500, "total_tokens": 2500}
    llm = GenericFakeChatModel(messages=iter([AIMessage(content="3.6 x 10^6 J [1]", usage_metadata=usage)]))

    result = answer("How many joules in 1 kW h?", store, llm, V2)

    assert result["cost"] == pytest.approx(0.00125)


def test_blank_question_raises_without_calling_the_model(store):
    store.add_texts(["Near point is 25 cm."], metadatas=[{"source": "eye.pdf", "page": 1}])
    recorder = Recorder()

    with pytest.raises(ValueError):
        answer("   ", store, recorder.llm, V2)
    assert recorder.prompts == []

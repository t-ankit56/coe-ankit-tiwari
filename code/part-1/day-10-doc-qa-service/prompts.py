"""Versioned prompts. PROMPT_VERSION picks one and defaults to v2."""
import os

from langchain_core.prompts import ChatPromptTemplate

HUMAN = ("human", "Context:\n{context}\n\nQuestion: {question}")

# v1: bare, no instructions.
V1 = ChatPromptTemplate.from_messages([HUMAN])

# v2: answer only from the chunks, cite them as [n], and say "I don't know" otherwise.
V2 = ChatPromptTemplate.from_messages([
    ("system",
     "Answer the question using only the numbered context chunks. "
     "Cite every chunk you use as [n], for example [1] or [2][3]. "
     "If the context does not contain the answer, reply exactly: I don't know."),
    HUMAN,
])

PROMPTS = {"v1": V1, "v2": V2}


def get_prompt() -> ChatPromptTemplate:
    version = os.environ.get("PROMPT_VERSION", "v2")
    if version not in PROMPTS:
        raise ValueError(f"Unknown PROMPT_VERSION: {version!r} (use v1 or v2)")
    return PROMPTS[version]

import os

from langchain_core.prompts import ChatPromptTemplate

V1 = ChatPromptTemplate.from_messages([
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])

V2 = ChatPromptTemplate.from_messages([
    ("system",
     "Answer the question using only the numbered context chunks. "
     "Cite every chunk you use as [n], for example [1] or [2][3]. "
     "If the context does not contain the answer, reply exactly: I don't know."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])


def get_prompt():
    version = os.environ.get("PROMPT_VERSION", "v2")
    if version == "v1":
        return V1
    if version == "v2":
        return V2
    raise ValueError(f"Unknown PROMPT_VERSION: {version!r} (use v1 or v2)")

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
    if os.environ.get("PROMPT_VERSION") == "v1":
        return V1
    return V2

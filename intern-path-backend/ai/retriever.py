from langchain_chroma import Chroma
from .embeddings import get_embeddings

_vectorstore = None
_retriever = None


def get_vector_store():
    global _vectorstore

    if _vectorstore is None:
        embeddings = get_embeddings()

        _vectorstore = Chroma(
            persist_directory="ai/vector_db",
            embedding_function=embeddings
        )

    return _vectorstore


def get_retriever():
    global _retriever

    if _retriever is None:
        vectordb = get_vector_store()
        _retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    return _retriever
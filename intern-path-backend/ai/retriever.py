_retriever = None


def get_retriever():
    global _retriever

    if _retriever is not None:
        return _retriever

    try:
        from langchain_chroma import Chroma
        from .embeddings import get_embeddings
    except Exception:
        _retriever = None
        return _retriever

    try:
        vectordb = Chroma(
            persist_directory="ai/vector_db",
            embedding_function=get_embeddings(),
        )
        _retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    except Exception:
        _retriever = None

    return _retriever
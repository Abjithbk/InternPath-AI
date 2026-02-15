from langchain_chroma import Chroma
from .embeddings import get_embeddings

def get_vector_store():
    embeddings = get_embeddings()

    vectordb = Chroma(
        persist_directory="ai/vector_db",
        embedding_function=embeddings
    )
    return vectordb

def get_retriever():
    vectordb = get_vector_store()
    return vectordb.as_retriever(search_kwargs={"k":3})
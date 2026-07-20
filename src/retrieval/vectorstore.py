from pathlib import Path

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from src.config.settings import EMBEDDING_MODEL

def get_embeddings() -> OpenAIEmbeddings:
     return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
    )

def create_or_update_vectorstore(
    documents: list[Document],
    persist_directory: str | Path,
    collection_name: str,
) -> Chroma:
      
    if not documents:
        raise ValueError(
            f"No documents provided for collection: {collection_name}"
        )
      
    persist_path = Path(persist_directory)
    persist_path.mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings()

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_path),
    )

    vectorstore.add_documents(documents)

    return vectorstore

def load_vectorstore(
    persist_directory: str |Path,
    collection_name: str,
) -> Chroma:
    
    embeddings = get_embeddings()
    
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_directory),
    )
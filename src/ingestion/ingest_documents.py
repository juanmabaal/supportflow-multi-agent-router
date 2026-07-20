from pathlib import Path

from src.config.settings import DATA_DIR, VECTORSTORES_DIR
from src.ingestion.document_loader import load_domain_documents
from src.ingestion.text_splitter import split_documents
from src.retrieval.vectorstore import create_or_update_vectorstore

DOMAIN_CONFIG = {
    "hr": {
        "documents_dir": DATA_DIR / "hr_docs",
        "persist_dir": VECTORSTORES_DIR / "hr",
        "collection_name": "hr_knowledge_base",
    },
    "tech": {
        "documents_dir": DATA_DIR / "tech_docs",
        "persist_dir": VECTORSTORES_DIR / "tech",
        "collection_name": "tech_knowledge_base",
    },
    "finance": {
        "documents_dir": DATA_DIR / "finance_docs",
        "persist_dir": VECTORSTORES_DIR / "finance",
        "collection_name": "finance_knowledge_base",
    },
    "legal": {
        "documents_dir": DATA_DIR / "legal_docs",
        "persist_dir": VECTORSTORES_DIR / "legal",
        "collection_name": "legal_knowledge_base",
    },
}


def ingest_domain(
    department: str,
    documents_dir: Path,
    persist_dir: Path,
    collection_name: str,
) -> None:
    print("=" * 80)
    print(f"Starting ingestion for domain: {department}")
    print(f"Documents directory: {documents_dir}")
    print(f"Vectorstore directory: {persist_dir}")
    print(f"Collection name: {collection_name}")

    documents = load_domain_documents(
        department=department,
        folder_path=documents_dir
    )

    if not documents:
        raise RuntimeError(
            f"No documents found for domain: {department}"
        )

    print(f"Loaded documents/pages: {len(documents)}")

    chunks = split_documents(documents)

    if not chunks:
        raise RuntimeError(
            f"No chunks created for domain: {department}"
        )

    print(f"Created chunks: {len(chunks)}")

    create_or_update_vectorstore(
        documents=chunks,
        persist_directory=persist_dir,
        collection_name=collection_name,
    )

    print(f"Vectorstore created successfully for domain: {department}")
    print("=" * 80)

def ingest_all_domains() -> None:
    for department, config in DOMAIN_CONFIG.items():
        ingest_domain(
            department=department,
            documents_dir=config["documents_dir"],
            persist_dir=config["persist_dir"],
            collection_name= config["collection_name"]
        )

if __name__ == "__main__":
    ingest_all_domains()
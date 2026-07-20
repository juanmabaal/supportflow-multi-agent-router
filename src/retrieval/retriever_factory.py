from src.config.settings import VECTORSTORES_DIR
from src.retrieval.vectorstore import load_vectorstore


DOMAIN_COLLECTIONS = {
    "hr": {
        "persist_dir": VECTORSTORES_DIR / "hr",
        "collection_name": "hr_knowledge_base",
    },
    "tech": {
        "persist_dir": VECTORSTORES_DIR / "tech",
        "collection_name": "tech_knowledge_base",
    },
    "finance": {
        "persist_dir": VECTORSTORES_DIR / "finance",
        "collection_name": "finance_knowledge_base",
    },
    "legal": {
        "persist_dir": VECTORSTORES_DIR / "legal",
        "collection_name": "legal_knowledge_base",
    },
}


def get_domain_vectorstore(department: str):
    if department not in DOMAIN_COLLECTIONS:
        raise ValueError(f"Unsupported department: {department}")

    config = DOMAIN_COLLECTIONS[department]

    return load_vectorstore(
        persist_directory=config["persist_dir"],
        collection_name=config["collection_name"],
    )


def get_domain_retriever(department: str, k: int = 4):
    vectorstore = get_domain_vectorstore(department)

    return vectorstore.as_retriever(
        search_kwargs={"k": k}
    )
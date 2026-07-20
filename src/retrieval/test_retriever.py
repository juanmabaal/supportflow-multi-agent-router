from src.retrieval.retriever_factory import get_domain_retriever


TEST_QUERIES = {
    "hr": "How can I request vacation days?",
    "tech": "I cannot connect to the VPN.",
    "finance": "How do I submit an expense reimbursement?",
    "legal": "Do I need legal approval before signing an NDA?",
}


def test_all_domain_retrievers() -> None:
    for department, query in TEST_QUERIES.items():
        print("=" * 100)
        print(f"Department: {department}")
        print(f"Query: {query}")

        retriever = get_domain_retriever(department, k=3)
        documents = retriever.invoke(query)

        print(f"Retrieved documents: {len(documents)}")

        for index, document in enumerate(documents, start=1):
            print("-" * 80)
            print(f"Result {index}")
            print("Chunk ID:", document.metadata.get("chunk_id"))
            print("Department:", document.metadata.get("department"))
            print("Source file:", document.metadata.get("source_file"))
            print("Page:", document.metadata.get("page"))
            print("Content preview:")
            print(document.page_content[:600])


if __name__ == "__main__":
    test_all_domain_retrievers()
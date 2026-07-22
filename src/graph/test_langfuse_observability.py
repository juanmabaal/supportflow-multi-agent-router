import json
from pathlib import Path

from src.config.settings import PROJECT_ROOT
from src.graph.graph_builder import run_supportflow_graph
from src.observability.langfuse_client import is_langfuse_configured

TEST_QUERIES_PATH = PROJECT_ROOT / "Test_queries.json"

def load_test_queries() -> list[dict]:
    if not TEST_QUERIES_PATH.exists():
        raise FileNotFoundError(
            f"Test queries file not found: {TEST_QUERIES_PATH}"
        )
    
    with TEST_QUERIES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_langfuse_observability_test() -> None:
    print("=" * 100)
    print("Testing Langfuse observability with SupportFlow graph")
    print("=" * 100)

    langfuse_enabled = is_langfuse_configured()

    print(f"Langfuse configured: {langfuse_enabled}")

    if not langfuse_enabled:
        print(
            "Langfuse keys are not configured. "
            "The graph will run without sending traces."
        )

    test_queries = load_test_queries()

    for index, test_case in enumerate(test_queries, start=1):
        query = test_case["query"]
        expected_department = test_case["expected_department"]

        print("-" * 100)
        print(f"Test case: {index}")
        print(f"Query: {query}")
        print(f"Expected department: {expected_department}")

        response = run_supportflow_graph(
            question=query,
            enable_observability=True,
            user_id="supportflow-test-user",
            session_id="supportflow-stage-6-validation",
        )

        print(f"Detected department: {response['detected_department']}")
        print(f"Agent: {response['agent_name']}")
        print(f"Sources: {len(response['sources'])}")
        print(f"Answer preview: {response['answer'][:300]}")

        assert response["detected_department"] == expected_department

    print("=" * 100)
    print("Langfuse observability validation completed.")
    print("=" * 100)


if __name__ == "__main__":
    run_langfuse_observability_test()
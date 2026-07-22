import json
from pathlib import Path

from src.config.settings import PROJECT_ROOT
from src.graph.graph_builder import run_supportflow_graph
from src.observability.langfuse_client import is_langfuse_configured


TEST_QUERIES_PATH = PROJECT_ROOT / "test_queries.json"


def load_test_queries() -> list[dict]:
    if not TEST_QUERIES_PATH.exists():
        raise FileNotFoundError(
            f"Test queries file not found: {TEST_QUERIES_PATH}"
        )

    with TEST_QUERIES_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_evaluator_with_graph_routes() -> None:
    print("=" * 100)
    print("Testing evaluator agent with LangGraph routes")
    print("=" * 100)

    print(f"Langfuse configured: {is_langfuse_configured()}")

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
            enable_scoring=True,
            user_id="supportflow-evaluator-test-user",
            session_id="supportflow-stage-7-evaluator-validation",
        )

        evaluation = response["evaluation"]

        print(f"Detected department: {response['detected_department']}")
        print(f"Agent: {response['agent_name']}")
        print(f"Sources: {len(response['sources'])}")
        print(f"Overall score: {evaluation['overall_score']}")
        print(f"Passed: {evaluation['passed']}")
        print(f"Risk level: {evaluation['risk_level']}")
        print(f"Scores recorded: {response['langfuse_scoring']['recorded']}")
        print(f"Scoring reason: {response['langfuse_scoring']['reason']}")
        print(f"Evaluation reason: {evaluation['reason']}")

        assert response["detected_department"] == expected_department
        assert 1 <= evaluation["overall_score"] <= 10
        assert evaluation["risk_level"] in ["low", "medium", "high"]

    print("=" * 100)
    print("Evaluator agent route validation completed.")
    print("=" * 100)


def test_low_quality_detection() -> None:
    print("=" * 100)
    print("Testing low-quality output detection")
    print("=" * 100)

    from src.agents.evaluator import evaluate_response_quality

    low_quality_response = {
        "user_question": "How do I submit an expense reimbursement?",
        "detected_department": "finance",
        "routing_confidence": 1.0,
        "routing_reason": "Matched finance keywords.",
        "matched_keywords": ["expense", "reimbursement"],
        "agent_name": "Finance Operations RAG Agent",
        "answer": "Just submit it.",
        "sources": [],
    }

    evaluation = evaluate_response_quality(low_quality_response)

    print(f"Overall score: {evaluation.overall_score}")
    print(f"Passed: {evaluation.passed}")
    print(f"Risk level: {evaluation.risk_level}")
    print(f"Reason: {evaluation.reason}")

    assert evaluation.overall_score < 7
    assert evaluation.passed is False
    assert evaluation.risk_level == "high"

    print("=" * 100)
    print("Low-quality output detection validation completed.")
    print("=" * 100)


if __name__ == "__main__":
    test_evaluator_with_graph_routes()
    test_low_quality_detection()
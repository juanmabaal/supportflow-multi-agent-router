from src.graph.graph_builder import run_supportflow_graph
from src.graph.router import classify_department


TEST_CASES = [
    {
        "query": "How can I request vacation days?",
        "expected_department": "hr",
    },
    {
        "query": "My manager has not approved my time off request.",
        "expected_department": "hr",
    },
    {
        "query": "I cannot connect to the VPN.",
        "expected_department": "tech",
    },
    {
        "query": "I received a suspicious phishing email.",
        "expected_department": "tech",
    },
    {
        "query": "How do I submit an expense reimbursement?",
        "expected_department": "finance",
    },
    {
        "query": "When will my invoice be paid?",
        "expected_department": "finance",
    },
    {
        "query": "Do I need legal approval before signing an NDA?",
        "expected_department": "legal",
    },
    {
        "query": "Who can sign a vendor contract?",
        "expected_department": "legal",
    },
    {
        "query": "Can you help me cook pasta?",
        "expected_department": "fallback",
    },
    {
        "query": "Can you explain the weather forecast for tomorrow?",
        "expected_department": "fallback",
    },
]


def test_router_only() -> None:
    print("=" * 100)
    print("Testing deterministic router only")
    print("=" * 100)

    for test_case in TEST_CASES:
        decision = classify_department(test_case["query"])

        print("-" * 100)
        print("Query:", test_case["query"])
        print("Expected:", test_case["expected_department"])
        print("Detected:", decision["department"])
        print("Confidence:", decision["confidence"])
        print("Reason:", decision["reason"])
        print("Matched keywords:", decision["matched_keywords"])

        assert decision["department"] == test_case["expected_department"]


def test_full_graph() -> None:
    print("=" * 100)
    print("Testing full LangGraph workflow")
    print("=" * 100)

    for test_case in TEST_CASES:
        print("-" * 100)
        print("Query:", test_case["query"])

        response = run_supportflow_graph(test_case["query"])

        print("Expected:", test_case["expected_department"])
        print("Detected:", response["detected_department"])
        print("Agent:", response["agent_name"])
        print("Confidence:", response["routing_confidence"])
        print("Answer:")
        print(response["answer"])
        print("Sources:", len(response["sources"]))

        assert response["detected_department"] == test_case["expected_department"]


if __name__ == "__main__":
    test_router_only()
    test_full_graph()
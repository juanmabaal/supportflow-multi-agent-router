from src.agents.finance_agent import answer_finance_question
from src.agents.hr_agent import answer_hr_question
from src.agents.legal_agent import answer_legal_question
from src.agents.tech_agent import answer_tech_question


TEST_CASES = [
    {
        "department": "hr",
        "question": "How can I request vacation days?",
        "runner": answer_hr_question,
    },
    {
        "department": "tech",
        "question": "I cannot connect to the VPN. What should I do?",
        "runner": answer_tech_question,
    },
    {
        "department": "finance",
        "question": "How do I submit an expense reimbursement?",
        "runner": answer_finance_question,
    },
    {
        "department": "legal",
        "question": "Do I need legal approval before signing an NDA?",
        "runner": answer_legal_question,
    },
]


def run_specialized_agent_tests() -> None:
    for test_case in TEST_CASES:
        print("=" * 100)
        print(f"Testing department: {test_case['department']}")
        print(f"Question: {test_case['question']}")

        response = test_case["runner"](test_case["question"])

        print("Department:", response.department)
        print("Agent:", response.agent_name)
        print("Answer:")
        print(response.answer)
        print("Sources:")

        for source in response.sources:
            print("-" * 80)
            print("Chunk ID:", source.chunk_id)
            print("Source file:", source.source_file)
            print("Score:", source.score)
            print("Preview:", source.content_preview[:300])


if __name__ == "__main__":
    run_specialized_agent_tests()
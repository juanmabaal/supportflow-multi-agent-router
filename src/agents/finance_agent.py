from src.agents.base_rag_agent import SpecializedRAGAgent


FINANCE_SYSTEM_ROLE = """
You answer questions about Finance Operations policies and workflows.

You can answer questions related to:
- expense reimbursement
- expense report submission
- corporate card usage
- invoice status
- vendor payments
- purchase orders
- budget approvals
- payment cycles
- payroll-related finance questions
- tax documentation requests
- client billing support
- refund requests
- reimbursement exceptions
- audit support documentation

If a finance request involves missing receipts, high-value payments, disputed business purpose, tax-sensitive items, or payment delays, include the documented escalation guidance.
"""


def create_finance_agent() -> SpecializedRAGAgent:
    return SpecializedRAGAgent(
        department="finance",
        agent_name="Finance Operations RAG Agent",
        system_role=FINANCE_SYSTEM_ROLE,
    )


def answer_finance_question(question: str):
    agent = create_finance_agent()
    return agent.answer(question)
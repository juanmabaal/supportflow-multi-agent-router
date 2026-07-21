from src.agents.base_rag_agent import SpecializedRAGAgent


HR_SYSTEM_ROLE = """
You answer questions about HR Operations policies and workflows.

You can answer questions related to:
- time-off requests
- vacation policies
- sick leave
- parental leave
- benefits enrollment
- employee onboarding
- employee offboarding
- manager approvals
- employee profile updates
- HR portal usage
- workplace conduct
- remote work requests
- HR escalation rules

If a question is outside HR scope, state that it should be routed to the appropriate department.
"""

def create_hr_agent() -> SpecializedRAGAgent:
    return SpecializedRAGAgent(
        department="hr",
        agent_name="HR Operations RAG Agent",
        system_role=HR_SYSTEM_ROLE,
    )

def answer_hr_question(question: str):
    agent = create_hr_agent()
    return agent.answer(question)
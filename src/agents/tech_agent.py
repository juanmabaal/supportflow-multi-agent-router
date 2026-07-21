from src.agents.base_rag_agent import SpecializedRAGAgent


TECH_SYSTEM_ROLE = """
You answer questions about IT Support and technical operations.

You can answer questions related to:
- password reset
- account lockout
- MFA issues
- VPN access
- email access
- laptop troubleshooting
- software installation
- hardware requests
- device replacement
- security incident reporting
- phishing emails
- internal portal access
- permission requests
- SaaS application access
- network connectivity
- remote work technical setup

If a question suggests suspicious activity, phishing, credential exposure, or repeated access failures, recommend escalation to Security Operations.
"""


def create_tech_agent() -> SpecializedRAGAgent:
    return SpecializedRAGAgent(
        department="tech",
        agent_name="IT Support RAG Agent",
        system_role=TECH_SYSTEM_ROLE,
    )


def answer_tech_question(question: str):
    agent = create_tech_agent()
    return agent.answer(question)
from typing import Callable

from langgraph.graph import END, START, StateGraph

from src.observability.langfuse_client import build_langfuse_config

from src.agents.finance_agent import answer_finance_question
from src.agents.hr_agent import answer_hr_question
from src.agents.legal_agent import answer_legal_question
from src.agents.tech_agent import answer_tech_question
from src.graph.router import orchestrator_node, route_by_department
from src.graph.state import SupportFlowState
from src.schemas.rag_response import RAGAgentResponse


AgentRunner = Callable[[str], RAGAgentResponse]


def serialize_agent_response(
    response: RAGAgentResponse,
    state: SupportFlowState,
) -> SupportFlowState:
    sources = [
        source.model_dump()
        for source in response.sources
    ]

    final_response = {
        "user_question": state["user_question"],
        "detected_department": state.get("detected_department"),
        "routing_confidence": state.get("routing_confidence"),
        "routing_reason": state.get("routing_reason"),
        "matched_keywords": state.get("matched_keywords", []),
        "agent_name": response.agent_name,
        "answer": response.answer,
        "sources": sources,
        "observability": {
        "provider": "langfuse",
        "traceable": True,
        },
    }

    return {
        **state,
        "agent_name": response.agent_name,
        "answer": response.answer,
        "sources": sources,
        "final_response": final_response,
        "error": None,
    }


def run_agent_node(
    state: SupportFlowState,
    agent_runner: AgentRunner,
) -> SupportFlowState:
    response = agent_runner(state["user_question"])

    return serialize_agent_response(
        response=response,
        state=state,
    )


def hr_agent_node(state: SupportFlowState) -> SupportFlowState:
    return run_agent_node(
        state=state,
        agent_runner=answer_hr_question,
    )


def tech_agent_node(state: SupportFlowState) -> SupportFlowState:
    return run_agent_node(
        state=state,
        agent_runner=answer_tech_question,
    )


def finance_agent_node(state: SupportFlowState) -> SupportFlowState:
    return run_agent_node(
        state=state,
        agent_runner=answer_finance_question,
    )


def legal_agent_node(state: SupportFlowState) -> SupportFlowState:
    return run_agent_node(
        state=state,
        agent_runner=answer_legal_question,
    )


def fallback_node(state: SupportFlowState) -> SupportFlowState:
    answer = (
        "I could not confidently route this question to HR, IT Support, "
        "Finance, or Legal based on the available routing rules. Please provide "
        "more details or select the appropriate department manually."
    )

    final_response = {
        "user_question": state["user_question"],
        "detected_department": "fallback",
        "routing_confidence": state.get("routing_confidence", 0.0),
        "routing_reason": state.get(
            "routing_reason",
            "The query could not be routed confidently.",
        ),
        "matched_keywords": state.get("matched_keywords", []),
        "agent_name": "Fallback Support Router",
        "answer": answer,
        "sources": [],
        "observability": {
        "provider": "langfuse",
        "traceable": True,
        },
    }

    return {
        **state,
        "detected_department": "fallback",
        "agent_name": "Fallback Support Router",
        "answer": answer,
        "sources": [],
        "final_response": final_response,
        "error": None,
    }


def build_supportflow_graph():
    graph = StateGraph(SupportFlowState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("hr_agent", hr_agent_node)
    graph.add_node("tech_agent", tech_agent_node)
    graph.add_node("finance_agent", finance_agent_node)
    graph.add_node("legal_agent", legal_agent_node)
    graph.add_node("fallback", fallback_node)

    graph.add_edge(START, "orchestrator")

    graph.add_conditional_edges(
        "orchestrator",
        route_by_department,
        {
            "hr_agent": "hr_agent",
            "tech_agent": "tech_agent",
            "finance_agent": "finance_agent",
            "legal_agent": "legal_agent",
            "fallback": "fallback",
        },
    )

    graph.add_edge("hr_agent", END)
    graph.add_edge("tech_agent", END)
    graph.add_edge("finance_agent", END)
    graph.add_edge("legal_agent", END)
    graph.add_edge("fallback", END)

    return graph.compile()


def run_supportflow_graph(
    question: str,
    enable_observability: bool = False,
    user_id: str | None = None,
    session_id: str | None = None,
) -> dict:
    app = build_supportflow_graph()

    initial_state: SupportFlowState = {
        "user_question": question,
    }
    
    config = {}

    if enable_observability:
        config = build_langfuse_config(
            trace_name="supportflow_langgraph_workflow",
            user_id=user_id,
            session_id=session_id,
            tags=[
                "supportflow",
                "langgraph",
                "multi-agent",
                "rag",
                "stage-6-observability",
            ],
            metadata={
                "component": "langgraph_orchestrator",
                "workflow": "supportflow_multi_agent_router",
                "stage": "stage_6_langfuse_observability",
            },
        )

    if config:
        final_state = app.invoke(
            initial_state,
            config=config,
        )
    else:
        final_state = app.invoke(initial_state)

    return final_state["final_response"]
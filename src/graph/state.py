from typing import Any, Literal, TypedDict

DepartmentRoute = Literal["hr", "tech", "finance", "legal", "fallback"]

class RoutingDecision(TypedDict):
    department: DepartmentRoute
    confidence: float
    reason: str
    matched_keywords: list[str]

class SupportFlowState(TypedDict, total=False):
    user_question: str

    user_id: str | None
    session_id: str | None
    trace_id: str | None
    enable_scoring: bool

    detected_department: DepartmentRoute
    routing_confidence: float
    routing_reason: str
    matched_keywords: list[str]

    agent_name: str
    answer: str
    sources: list[dict[str, Any]]

    evaluation: dict[str, Any]
    evaluation_recorded: bool
    evaluation_error: str | None

    final_response: dict[str, Any]
    error: str | None
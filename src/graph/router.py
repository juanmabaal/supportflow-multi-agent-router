import re

from src.graph.state import DepartmentRoute, RoutingDecision, SupportFlowState


DEPARTMENT_KEYWORDS: dict[DepartmentRoute, list[str]] = {
    "hr": [
        "vacation",
        "time off",
        "pto",
        "sick leave",
        "parental leave",
        "benefits",
        "health insurance",
        "onboarding",
        "offboarding",
        "employee profile",
        "manager approval",
        "workplace conduct",
        "remote work",
        "leave request",
        "peoplehub",
    ],
    "tech": [
        "password",
        "vpn",
        "mfa",
        "multi-factor",
        "account locked",
        "login",
        "email access",
        "laptop",
        "software",
        "hardware",
        "device",
        "phishing",
        "security incident",
        "portal access",
        "permission",
        "network",
        "secureconnect",
    ],
    "finance": [
        "expense",
        "reimbursement",
        "invoice",
        "payment",
        "vendor payment",
        "purchase order",
        "po",
        "budget",
        "corporate card",
        "receipt",
        "refund",
        "billing",
        "tax document",
        "financehub",
        "expense center",
    ],
    "legal": [
        "contract",
        "nda",
        "legal approval",
        "vendor agreement",
        "customer agreement",
        "terms and conditions",
        "signature",
        "signatory",
        "data privacy",
        "compliance",
        "document retention",
        "intellectual property",
        "ip",
        "security addendum",
        "privacy addendum",
        "legalhub",
    ],
    "fallback": [],
}

ROUTE_TO_NODE: dict[DepartmentRoute, str] = {
    "hr": "hr_agent",
    "tech": "tech_agent",
    "finance": "finance_agent",
    "legal": "legal_agent",
    "fallback": "fallback",
}

def normalize_text(text: str) -> str:
    normalized = text.lower()
    normalized = re.sub(r"[^a-z0-9\s\-]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized

def find_keyword_matches(question: str, keywords: list[str]) -> list[str]:
    normalized_question = normalize_text(question)
    matches = []

    for keyword in keywords:
        normalized_keyword = normalize_text(keyword)

        if normalized_keyword in normalized_question:
            matches.append(keyword)

    return matches

def classify_department(question: str) -> RoutingDecision:
    scores: dict[DepartmentRoute, int] = {}
    matches_by_department: dict[DepartmentRoute, list[str]] = {}

    for department, keywords in DEPARTMENT_KEYWORDS.items():
        if department == "fallback":
            continue

        matches = find_keyword_matches(question, keywords)
        matches_by_department[department] = matches
        scores[department] = len(matches)

    max_score = max(scores.values(), default=0)

    if max_score == 0:
        return RoutingDecision(
            department="fallback",
            confidence=0.0,
            reason="No domain-specific keywords were detected.",
            matched_keywords=[],
        )

    top_departments = [
        department
        for department, score in scores.items()
        if score == max_score
    ]

    if len(top_departments) > 1:
        return RoutingDecision(
            department="fallback",
            confidence=0.0,
            reason=(
                "Ambiguous query. Multiple departments matched with the same score: "
                f"{', '.join(top_departments)}."
            ),
            matched_keywords=[],
        )

    selected_department = top_departments[0]
    total_matches = sum(scores.values())

    confidence = round(
        max_score / total_matches,
        2,
    ) if total_matches > 0 else 0.0

    return RoutingDecision(
        department=selected_department,
        confidence=confidence,
        reason=(
            f"Matched {max_score} keyword(s) for department '{selected_department}'."
        ),
        matched_keywords=matches_by_department[selected_department],
    )


def orchestrator_node(state: SupportFlowState) -> SupportFlowState:
    question = state["user_question"]

    decision = classify_department(question)

    return {
        **state,
        "detected_department": decision["department"],
        "routing_confidence": decision["confidence"],
        "routing_reason": decision["reason"],
        "matched_keywords": decision["matched_keywords"],
    }


def route_by_department(state: SupportFlowState) -> str:
    department = state.get("detected_department", "fallback")

    return ROUTE_TO_NODE.get(department, "fallback")
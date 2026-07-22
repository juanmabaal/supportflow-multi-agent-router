import json
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st


# =============================================================================
# PROJECT IMPORTS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.graph.graph_builder import run_supportflow_graph
from src.observability.langfuse_client import is_langfuse_configured


# =============================================================================
# BRAND CONSTANTS
# =============================================================================

BRAND_NAVY = "#102840"
BRAND_NAVY_SOFT = "#163A59"
BRAND_TEAL = "#087870"
BRAND_TEAL_SOFT = "#0B8F84"
BRAND_YELLOW = "#F0C048"
BRAND_WHITE = "#FFFFFF"
BRAND_MUTED = "#BFD6DF"
BRAND_CARD = "rgba(255, 255, 255, 0.08)"
BRAND_BORDER = "rgba(240, 192, 72, 0.35)"


DOMAIN_LABELS = {
    "hr": "HR Operations",
    "tech": "IT Support",
    "finance": "Finance Operations",
    "legal": "Legal Operations",
    "fallback": "Fallback Router",
}

DOMAIN_ICONS = {
    "hr": "👥",
    "tech": "🛠️",
    "finance": "💳",
    "legal": "⚖️",
    "fallback": "🧭",
}

DOMAIN_COLORS = {
    "hr": "#8FD3FF",
    "tech": "#B4F8C8",
    "finance": BRAND_YELLOW,
    "legal": "#D8B4FE",
    "fallback": "#CBD5E1",
}


# =============================================================================
# STREAMLIT PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="SupportFlow Multi-Agent Router",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# CUSTOM CSS
# =============================================================================

st.markdown(
    f"""
    <style>
        :root {{
            --brand-navy: {BRAND_NAVY};
            --brand-navy-soft: {BRAND_NAVY_SOFT};
            --brand-teal: {BRAND_TEAL};
            --brand-teal-soft: {BRAND_TEAL_SOFT};
            --brand-yellow: {BRAND_YELLOW};
            --brand-white: {BRAND_WHITE};
            --brand-muted: {BRAND_MUTED};
            --brand-card: {BRAND_CARD};
            --brand-border: {BRAND_BORDER};
        }}

        /* =============================================================================
           GLOBAL APP BACKGROUND
           ============================================================================= */

        .stApp {{
            background:
                radial-gradient(circle at 92% 8%, rgba(240, 192, 72, 0.22) 0, transparent 18%),
                linear-gradient(135deg, var(--brand-navy) 0%, var(--brand-navy) 62%, var(--brand-teal) 100%);
            color: var(--brand-white) !important;
        }}

        html, body, [class*="css"] {{
            color: var(--brand-white) !important;
        }}

        p, span, div, label, small {{
            color: rgba(255, 255, 255, 0.92) !important;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: var(--brand-white) !important;
        }}

        strong, b {{
            color: var(--brand-yellow) !important;
        }}

        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }}

        /* =============================================================================
           SIDEBAR
           ============================================================================= */

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0B2339 0%, #0A4F4B 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.12);
        }}

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] div {{
            color: rgba(255, 255, 255, 0.92) !important;
        }}

        .sidebar-brand {{
            padding: 1rem 0.2rem 0.4rem 0.2rem;
        }}

        .sidebar-title {{
            font-size: 1.3rem;
            font-weight: 850;
            color: var(--brand-white) !important;
            line-height: 1.1;
        }}

        .sidebar-subtitle {{
            color: rgba(255, 255, 255, 0.78) !important;
            font-size: 0.86rem;
            margin-top: 0.35rem;
        }}

        .domain-mini {{
            padding: 0.7rem 0.8rem;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            margin-bottom: 0.55rem;
            font-weight: 750;
            color: var(--brand-white) !important;
        }}

        /* =============================================================================
           HERO CARD
           ============================================================================= */

        .hero-card {{
            position: relative;
            padding: 2.2rem 2.4rem;
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(255, 255, 255, 0.10), rgba(255, 255, 255, 0.035)),
                linear-gradient(135deg, rgba(16, 40, 64, 0.92), rgba(8, 120, 112, 0.78));
            border: 1px solid rgba(255, 255, 255, 0.16);
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.28);
            overflow: hidden;
            margin-bottom: 1.3rem;
        }}

        .hero-card::after {{
            content: "+";
            position: absolute;
            right: 3rem;
            top: 1.8rem;
            width: 116px;
            height: 116px;
            border-radius: 999px;
            background: var(--brand-yellow);
            color: var(--brand-navy);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 5.4rem;
            font-weight: 200;
            line-height: 1;
            box-shadow: 0 18px 45px rgba(0, 0, 0, 0.18);
        }}

        .eyebrow {{
            color: var(--brand-yellow) !important;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-size: 0.92rem;
            margin-bottom: 0.7rem;
        }}

        .hero-title {{
            color: var(--brand-white) !important;
            font-size: 3.15rem;
            line-height: 1.02;
            font-weight: 850;
            max-width: 780px;
            margin: 0;
        }}

        .hero-subtitle {{
            color: rgba(255, 255, 255, 0.88) !important;
            font-size: 1.08rem;
            margin-top: 1rem;
            max-width: 760px;
        }}

        .status-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            margin-top: 1.4rem;
        }}

        .status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.48rem 0.8rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.16);
            color: var(--brand-white) !important;
            font-size: 0.84rem;
            font-weight: 650;
        }}

        /* =============================================================================
           PANELS AND CARDS
           ============================================================================= */

        .panel {{
            padding: 1.1rem 1.2rem;
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.075);
            border: 1px solid rgba(255, 255, 255, 0.13);
            box-shadow: 0 14px 42px rgba(0, 0, 0, 0.16);
            margin-bottom: 1rem;
            color: var(--brand-white) !important;
        }}

        .panel-title {{
            color: var(--brand-yellow) !important;
            font-weight: 800;
            font-size: 0.82rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
        }}

        .route-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.45rem 0.72rem;
            border-radius: 999px;
            font-weight: 800;
            background: rgba(240, 192, 72, 0.16);
            color: var(--brand-yellow) !important;
            border: 1px solid rgba(240, 192, 72, 0.45);
            margin-bottom: 0.75rem;
        }}

        .answer-card {{
            padding: 1rem 1.05rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.085);
            border: 1px solid rgba(255, 255, 255, 0.16);
            color: rgba(255, 255, 255, 0.95) !important;
        }}

        .source-card {{
            padding: 0.8rem 0.95rem;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.085);
            border: 1px solid rgba(255, 255, 255, 0.16);
            margin-bottom: 0.7rem;
            color: rgba(255, 255, 255, 0.94) !important;
        }}

        .source-title {{
            color: var(--brand-yellow) !important;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }}

        .muted {{
            color: rgba(255, 255, 255, 0.82) !important;
            font-size: 0.9rem;
        }}

        .footer-note {{
            color: rgba(255, 255, 255, 0.72) !important;
            font-size: 0.82rem;
            text-align: center;
            margin-top: 1rem;
        }}

        .finalized-box {{
            padding: 1rem 1.1rem;
            border-radius: 18px;
            background: rgba(240, 192, 72, 0.16);
            border: 1px solid rgba(240, 192, 72, 0.44);
            color: var(--brand-white) !important;
            margin-bottom: 1rem;
        }}

        /* =============================================================================
           MARKDOWN TEXT
           ============================================================================= */

        [data-testid="stMarkdownContainer"] {{
            color: rgba(255, 255, 255, 0.94) !important;
        }}

        [data-testid="stMarkdownContainer"] p {{
            color: rgba(255, 255, 255, 0.94) !important;
            line-height: 1.7;
        }}

        [data-testid="stMarkdownContainer"] li {{
            color: rgba(255, 255, 255, 0.92) !important;
        }}

        /* =============================================================================
           CHAT MESSAGES
           ============================================================================= */

        div[data-testid="stChatMessage"] {{
            background: rgba(255, 255, 255, 0.085) !important;
            border: 1px solid rgba(255, 255, 255, 0.16) !important;
            border-radius: 22px;
            padding: 0.75rem;
        }}

        div[data-testid="stChatMessage"] p {{
            color: rgba(255, 255, 255, 0.95) !important;
            font-size: 1rem;
            line-height: 1.75;
        }}

        div[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
            color: rgba(255, 255, 255, 0.95) !important;
        }}

        /* =============================================================================
           METRICS
           ============================================================================= */

        div[data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.09);
            border: 1px solid rgba(255, 255, 255, 0.16);
            border-radius: 18px;
            padding: 0.8rem 0.9rem;
        }}

        div[data-testid="stMetricLabel"] p {{
            color: rgba(255, 255, 255, 0.78) !important;
            font-weight: 600;
        }}

        div[data-testid="stMetricValue"] {{
            color: var(--brand-white) !important;
        }}

        div[data-testid="stMetricValue"] div {{
            color: var(--brand-white) !important;
        }}

        /* =============================================================================
           EXPANDERS
           ============================================================================= */

        [data-testid="stExpander"] {{
            background: rgba(255, 255, 255, 0.075) !important;
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            border-radius: 16px !important;
            margin-bottom: 0.75rem;
        }}

        [data-testid="stExpander"] details summary {{
            color: var(--brand-yellow) !important;
            font-weight: 750 !important;
        }}

        [data-testid="stExpander"] p,
        [data-testid="stExpander"] span,
        [data-testid="stExpander"] div {{
            color: rgba(255, 255, 255, 0.92) !important;
        }}

        /* =============================================================================
           BUTTONS
           ============================================================================= */

        .stButton > button {{
            border-radius: 999px;
            border: 1px solid rgba(240, 192, 72, 0.45);
            background: rgba(240, 192, 72, 0.13);
            color: var(--brand-white) !important;
            font-weight: 750;
            transition: all 0.2s ease;
        }}

        .stButton > button:hover {{
            border-color: var(--brand-yellow);
            background: rgba(240, 192, 72, 0.24);
            color: var(--brand-yellow) !important;
            transform: translateY(-1px);
        }}

        [data-testid="stDownloadButton"] button {{
            color: var(--brand-white) !important;
        }}

        /* =============================================================================
           CHAT INPUT
           ============================================================================= */

        div[data-testid="stChatInput"] {{
            background: rgba(255, 255, 255, 0.96) !important;
            border: 1px solid rgba(240, 192, 72, 0.65) !important;
            border-radius: 18px !important;
        }}

        div[data-testid="stChatInput"] textarea {{
            color: var(--brand-navy) !important;
            background: transparent !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stChatInput"] textarea::placeholder {{
            color: rgba(16, 40, 64, 0.55) !important;
        }}

        div[data-testid="stChatInput"] button {{
            background: var(--brand-yellow) !important;
            color: var(--brand-navy) !important;
            border-radius: 14px !important;
            border: none !important;
        }}

        div[data-testid="stChatInput"] button svg {{
            color: var(--brand-navy) !important;
            fill: var(--brand-navy) !important;
        }}

        /* =============================================================================
           ALERTS AND CODE
           ============================================================================= */

        [data-testid="stAlert"] {{
            background: rgba(255, 255, 255, 0.10) !important;
            color: var(--brand-white) !important;
            border-radius: 16px !important;
        }}

        [data-testid="stAlert"] p {{
            color: var(--brand-white) !important;
        }}

        code {{
            color: var(--brand-yellow) !important;
            background: rgba(0, 0, 0, 0.24) !important;
            border-radius: 6px;
        }}

        /* =============================================================================
           RESPONSIVE
           ============================================================================= */

        @media (max-width: 900px) {{
            .hero-title {{
                font-size: 2.25rem;
            }}

            .hero-card::after {{
                width: 78px;
                height: 78px;
                font-size: 3.5rem;
                right: 1.2rem;
                top: 1.2rem;
            }}
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# SESSION STATE
# =============================================================================

def initialize_session_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"supportflow-ui-{uuid.uuid4()}"

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Welcome to SupportFlow. Ask an internal support question and "
                    "I will route it to the right specialized RAG agent."
                ),
                "response": None,
            }
        ]

    if "chat_finalized" not in st.session_state:
        st.session_state.chat_finalized = False

    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0

    if "last_department" not in st.session_state:
        st.session_state.last_department = "None"

    if "last_score" not in st.session_state:
        st.session_state.last_score = "N/A"


def reset_chat() -> None:
    st.session_state.session_id = f"supportflow-ui-{uuid.uuid4()}"
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "New session started. Ask a support question and I will route it "
                "through the multi-agent workflow."
            ),
            "response": None,
        }
    ]
    st.session_state.chat_finalized = False
    st.session_state.total_questions = 0
    st.session_state.last_department = "None"
    st.session_state.last_score = "N/A"


def finalize_chat() -> None:
    st.session_state.chat_finalized = True
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": (
                "This chat session has been finalized. Start a new chat to continue "
                "with another support conversation."
            ),
            "response": None,
        }
    )


initialize_session_state()


# =============================================================================
# DATA HELPERS
# =============================================================================

def load_test_queries() -> list[dict[str, str]]:
    test_queries_path = PROJECT_ROOT / "test_queries.json"

    fallback_queries = [
        {
            "query": "How can I request vacation days?",
            "expected_department": "hr",
        },
        {
            "query": "I cannot connect to the VPN.",
            "expected_department": "tech",
        },
        {
            "query": "How do I submit an expense reimbursement?",
            "expected_department": "finance",
        },
        {
            "query": "Do I need legal approval before signing an NDA?",
            "expected_department": "legal",
        },
        {
            "query": "Can you help me cook pasta?",
            "expected_department": "fallback",
        },
    ]

    if not test_queries_path.exists():
        return fallback_queries

    try:
        with test_queries_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return fallback_queries


def format_department(department: str | None) -> str:
    if not department:
        return "Unknown"

    icon = DOMAIN_ICONS.get(department, "🧭")
    label = DOMAIN_LABELS.get(department, department.title())

    return f"{icon} {label}"


def get_risk_emoji(risk_level: str | None) -> str:
    if risk_level == "low":
        return "🟢"

    if risk_level == "medium":
        return "🟡"

    if risk_level == "high":
        return "🔴"

    return "⚪"


def build_conversation_export() -> str:
    export_payload = {
        "session_id": st.session_state.session_id,
        "exported_at": datetime.utcnow().isoformat(),
        "messages": st.session_state.messages,
    }

    return json.dumps(export_payload, indent=2, ensure_ascii=False)


# =============================================================================
# RENDER HELPERS
# =============================================================================

def render_hero() -> None:
    langfuse_status = "Enabled" if is_langfuse_configured() else "Not configured"

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="eyebrow">Enterprise Support Operations</div>
            <h1 class="hero-title">SupportFlow Multi-Agent Router</h1>
            <div class="hero-subtitle">
                A branded RAG command center for HR, IT Support, Finance and Legal workflows.
                The system routes questions, retrieves grounded context, evaluates answer quality
                and records observability metrics.
            </div>
            <div class="status-row">
                <div class="status-pill">🧠 LangGraph Workflow</div>
                <div class="status-pill">📚 Specialized RAG Agents</div>
                <div class="status-pill">🧪 Evaluator Agent</div>
                <div class="status-pill">📈 Langfuse: {langfuse_status}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-title">SupportFlow</div>
            <div class="sidebar-subtitle">
                Internal multi-agent RAG router
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.divider()

    st.sidebar.markdown("### Session Controls")

    col_a, col_b = st.sidebar.columns(2)

    with col_a:
        if st.button("New chat", use_container_width=True):
            reset_chat()
            st.rerun()

    with col_b:
        if st.button("End chat", use_container_width=True, disabled=st.session_state.chat_finalized):
            finalize_chat()
            st.rerun()

    st.sidebar.caption(f"Session ID: `{st.session_state.session_id}`")

    st.sidebar.divider()

    st.sidebar.markdown("### Live Session")

    st.sidebar.metric("Questions", st.session_state.total_questions)
    st.sidebar.metric("Last route", st.session_state.last_department)
    st.sidebar.metric("Last score", st.session_state.last_score)

    st.sidebar.divider()

    st.sidebar.markdown("### Specialized Agents")

    for department in ["hr", "tech", "finance", "legal", "fallback"]:
        st.sidebar.markdown(
            f"""
            <div class="domain-mini">
                {format_department(department)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.divider()

    st.sidebar.markdown("### Export")

    st.sidebar.download_button(
        label="Download chat JSON",
        data=build_conversation_export(),
        file_name=f"{st.session_state.session_id}.json",
        mime="application/json",
        use_container_width=True,
    )


def render_quick_prompts() -> None:
    test_queries = load_test_queries()

    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Quick route tests</div>
            <div class="muted">
                These prompts are loaded from test_queries.json, the same test source used in graph validation.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(2)

    for index, test_case in enumerate(test_queries[:10]):
        department = test_case.get("expected_department", "fallback")
        query = test_case.get("query", "")

        with columns[index % 2]:
            button_label = f"{DOMAIN_ICONS.get(department, '🧭')} {query}"

            if st.button(
                button_label,
                key=f"quick_prompt_{index}",
                use_container_width=True,
                disabled=st.session_state.chat_finalized,
            ):
                st.session_state.queued_prompt = query
                st.rerun()


def render_response_metadata(response: dict[str, Any]) -> None:
    department = response.get("detected_department", "fallback")
    department_label = format_department(department)
    confidence = response.get("routing_confidence", 0.0)
    sources = response.get("sources", [])
    evaluation = response.get("evaluation", {})
    scoring = response.get("langfuse_scoring", {})

    overall_score = evaluation.get("overall_score", "N/A")
    risk_level = evaluation.get("risk_level", "unknown")
    passed = evaluation.get("passed", None)

    st.markdown(
        f"""
        <div class="route-badge">
            {department_label}
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_1, col_2, col_3, col_4 = st.columns(4)

    with col_1:
        st.metric("Routing confidence", confidence)

    with col_2:
        st.metric("Sources", len(sources))

    with col_3:
        st.metric("Quality score", overall_score)

    with col_4:
        pass_label = "Passed" if passed else "Review"
        st.metric("Evaluation", f"{get_risk_emoji(risk_level)} {pass_label}")

    with st.expander("Routing details", expanded=False):
        st.write("**Agent:**", response.get("agent_name"))
        st.write("**Reason:**", response.get("routing_reason"))
        st.write("**Matched keywords:**", response.get("matched_keywords", []))

    if evaluation:
        with st.expander("Evaluator Agent", expanded=False):
            st.write("**Overall score:**", evaluation.get("overall_score"))
            st.write("**Risk level:**", evaluation.get("risk_level"))
            st.write("**Passed:**", evaluation.get("passed"))
            st.write("**Reason:**", evaluation.get("reason"))

            suggestions = evaluation.get("improvement_suggestions", [])

            if suggestions:
                st.write("**Improvement suggestions:**")
                for suggestion in suggestions:
                    st.write(f"- {suggestion}")

            score_cols = st.columns(5)

            dimensions = [
                ("Relevance", evaluation.get("relevance")),
                ("Completeness", evaluation.get("completeness")),
                ("Accuracy", evaluation.get("accuracy")),
                ("Groundedness", evaluation.get("groundedness")),
                ("Clarity", evaluation.get("clarity")),
            ]

            for column, (label, value) in zip(score_cols, dimensions):
                with column:
                    st.metric(label, value)

    if scoring:
        with st.expander("Langfuse scoring", expanded=False):
            st.write("**Recorded:**", scoring.get("recorded"))
            st.write("**Reason:**", scoring.get("reason"))


def render_sources(response: dict[str, Any]) -> None:
    sources = response.get("sources", [])

    if not sources:
        st.info("No retrieved sources were used for this response.")
        return

    with st.expander("Retrieved sources", expanded=False):
        for index, source in enumerate(sources, start=1):
            st.markdown(
                f"""
                <div class="source-card">
                    <div class="source-title">Source {index}: {source.get("chunk_id", "unknown")}</div>
                    <div class="muted">
                        Department: {source.get("department", "unknown")}<br>
                        File: {source.get("source_file", "unknown")}<br>
                        Retrieval score: {source.get("score", "N/A")}
                    </div>
                    <br>
                    {source.get("content_preview", "")}
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_chat_history() -> None:
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        content = message.get("content", "")
        response = message.get("response")

        avatar = "👤" if role == "user" else "🧠"

        with st.chat_message(role, avatar=avatar):
            st.markdown(content)

            if response:
                render_response_metadata(response)
                render_sources(response)


def process_user_prompt(prompt: str) -> None:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
            "response": None,
        }
    )

    with st.spinner("Routing question through SupportFlow agents..."):
        response = run_supportflow_graph(
            question=prompt,
            enable_observability=True,
            enable_scoring=True,
            user_id="supportflow-streamlit-user",
            session_id=st.session_state.session_id,
        )

    answer = response.get(
        "answer",
        "The system did not return an answer.",
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "response": response,
        }
    )

    st.session_state.total_questions += 1

    detected_department = response.get("detected_department", "fallback")
    st.session_state.last_department = DOMAIN_LABELS.get(
        detected_department,
        detected_department,
    )

    evaluation = response.get("evaluation", {})
    st.session_state.last_score = str(evaluation.get("overall_score", "N/A"))


# =============================================================================
# MAIN APP
# =============================================================================

render_sidebar()
render_hero()

if st.session_state.chat_finalized:
    st.markdown(
        """
        <div class="finalized-box">
            <strong>Chat finalized.</strong><br>
            The current conversation is closed. Use <strong>New chat</strong> from the sidebar to start another session.
        </div>
        """,
        unsafe_allow_html=True,
    )

render_quick_prompts()

st.divider()

render_chat_history()

queued_prompt = st.session_state.pop("queued_prompt", None)

typed_prompt = st.chat_input(
    "Ask a question about HR, IT Support, Finance or Legal...",
    disabled=st.session_state.chat_finalized,
)

prompt = queued_prompt or typed_prompt

if prompt and not st.session_state.chat_finalized:
    process_user_prompt(prompt)
    st.rerun()

st.markdown(
    """
    <div class="footer-note">
        SupportFlow Multi-Agent Router · LangGraph · RAG · Langfuse · Evaluator Agent
    </div>
    """,
    unsafe_allow_html=True,
)
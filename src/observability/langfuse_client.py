import os
from typing import Any

from langfuse.langchain import CallbackHandler

from langfuse import get_client
from src.schemas.evaluation import EvaluationResult

from src.config.settings import (
    LANGFUSE_ENVIRONMENT,
    LANGFUSE_HOST,
    LANGFUSE_PUBLIC_KEY,
    LANGFUSE_RELEASE,
    LANGFUSE_SECRET_KEY,
)


def is_langfuse_configured() -> bool:
    return bool(
        LANGFUSE_PUBLIC_KEY
        and LANGFUSE_SECRET_KEY
        and LANGFUSE_HOST
    )


def configure_langfuse_environment() -> None:
    if not is_langfuse_configured():
        return

    os.environ["LANGFUSE_PUBLIC_KEY"] = LANGFUSE_PUBLIC_KEY
    os.environ["LANGFUSE_SECRET_KEY"] = LANGFUSE_SECRET_KEY


    os.environ["LANGFUSE_BASE_URL"] = LANGFUSE_HOST
    os.environ["LANGFUSE_HOST"] = LANGFUSE_HOST

    os.environ["LANGFUSE_RELEASE"] = LANGFUSE_RELEASE
    os.environ["LANGFUSE_TRACING_ENVIRONMENT"] = LANGFUSE_ENVIRONMENT


def get_langfuse_callback_handler() -> CallbackHandler | None:
    if not is_langfuse_configured():
        return None

    configure_langfuse_environment()

    return CallbackHandler()


def build_langfuse_config(
    trace_name: str,
    user_id: str | None = None,
    session_id: str | None = None,
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> dict:
    handler = get_langfuse_callback_handler()

    if handler is None:
        return {}

    return {
        "callbacks": [handler],
        "metadata": {
            "trace_name": trace_name,
            "environment": LANGFUSE_ENVIRONMENT,
            "release": LANGFUSE_RELEASE,
            "user_id": user_id,
            "session_id": session_id,
            **(metadata or {}),
        },
        "tags": tags or [],
    }

def get_langfuse_client():
    if not is_langfuse_configured():
        return None

    configure_langfuse_environment()

    return get_client()


def flush_langfuse() -> None:
    client = get_langfuse_client()

    if client is None:
        return

    if hasattr(client, "flush"):
        client.flush()


def record_evaluation_scores(
    evaluation: EvaluationResult,
    session_id: str | None,
    trace_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    client = get_langfuse_client()

    if client is None:
        return {
            "recorded": False,
            "reason": "Langfuse is not configured.",
        }

    if not session_id and not trace_id:
        return {
            "recorded": False,
            "reason": "No session_id or trace_id was provided for scoring.",
        }

    score_metadata = metadata or {}

    score_payloads = [
        ("eval_relevance", float(evaluation.relevance)),
        ("eval_completeness", float(evaluation.completeness)),
        ("eval_accuracy", float(evaluation.accuracy)),
        ("eval_groundedness", float(evaluation.groundedness)),
        ("eval_clarity", float(evaluation.clarity)),
        ("eval_overall_quality", float(evaluation.overall_score)),
    ]

    try:
        for score_name, score_value in score_payloads:
            client.create_score(
                name=score_name,
                value=score_value,
                session_id=session_id,
                trace_id=trace_id,
                data_type="NUMERIC",
                comment=evaluation.reason[:500],
                metadata={
                    **score_metadata,
                    "passed": evaluation.passed,
                    "risk_level": evaluation.risk_level,
                },
            )

        client.create_score(
            name="eval_passed",
            value=1.0 if evaluation.passed else 0.0,
            session_id=session_id,
            trace_id=trace_id,
            data_type="BOOLEAN",
            comment=evaluation.reason[:500],
            metadata={
                **score_metadata,
                "overall_score": evaluation.overall_score,
                "risk_level": evaluation.risk_level,
            },
        )

        flush_langfuse()

        return {
            "recorded": True,
            "reason": "Evaluation scores were recorded in Langfuse.",
        }

    except Exception as error:
        return {
            "recorded": False,
            "reason": str(error),
        }
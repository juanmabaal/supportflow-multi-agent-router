import os

from langfuse.langchain import CallbackHandler

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
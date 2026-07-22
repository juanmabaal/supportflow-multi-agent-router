import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
VECTORSTORES_DIR = PROJECT_ROOT /"vectorstores"

#LLM PROVIDER

SUPPORTED_LLM_PROVIDERS = {"openai", "xai", "deepseek"}

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
LLM_FALLBACK_PROVIDER = os.getenv("LLM_FALLBACK_PROVIDER", "openai").lower()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
XAI_MODEL = os.getenv("XAI_MODEL", "grok-4.3")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


# EMBEDDING SETTINGS
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "text-embedding-3-small",
)

# LANGFUSE SETTINGS
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv(
    "LANGFUSE_BASE_URL",
    "https://cloud.langfuse.com",
)

LANGFUSE_ENVIRONMENT = os.getenv(
    "LANGFUSE_ENVIRONMENT",
    "development",
)

LANGFUSE_RELEASE = os.getenv(
    "LANGFUSE_RELEASE",
    "supportflow-local",
)


# Evaluator settings
EVALUATION_PASS_THRESHOLD = float(
    os.getenv("EVALUATION_PASS_THRESHOLD", "7.0")
)

ENABLE_LANGFUSE_SCORING = (
    os.getenv("ENABLE_LANGFUSE_SCORING", "true").lower() == "true"
)

def validate_llm_provider(provider: str) -> str:
    normalized_provider = provider.lower()

    if normalized_provider not in SUPPORTED_LLM_PROVIDERS:
          raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers are: {sorted(SUPPORTED_LLM_PROVIDERS)}"
        )
    return normalized_provider
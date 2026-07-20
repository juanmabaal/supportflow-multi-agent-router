from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_xai import ChatXAI
from langchain_deepseek import ChatDeepSeek

from src.config.settings import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_MODEL,
    LLM_FALLBACK_PROVIDER,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    XAI_API_KEY,
    XAI_MODEL,
    validate_llm_provider,
)

DEFAULT_TEMPERATURE = 0

class LLMProviderError(RuntimeError):
    """Raised when a chat model provider cannot be initialized."""


def _build_openai_model(
    temperature: float = DEFAULT_TEMPERATURE,
    **kwargs: Any,
) -> BaseChatModel:
    
    if not OPENAI_API_KEY:
        raise LLMProviderError("OPENAI_API_KEY is required for OpenAI provider.")
    
    return ChatOpenAI(
        model = OPENAI_MODEL,
        temperature=temperature,
        api_key=OPENAI_API_KEY,
        **kwargs,
    )

def _build_xai_model(
    temperature: float = DEFAULT_TEMPERATURE,
    **kwargs: Any,
) -> BaseChatModel:
    if not XAI_API_KEY:
        raise LLMProviderError("XAI_API_KEY is required for xAI provider.")

    return ChatXAI(
        model=XAI_MODEL,
        temperature=temperature,
        api_key=XAI_API_KEY,
        **kwargs,
    )

def _build_deepseek_model(
    temperature: float = DEFAULT_TEMPERATURE,
    **kwargs: Any,
) -> BaseChatModel:
    if not DEEPSEEK_API_KEY:
        raise LLMProviderError("DEEPSEEK_API_KEY is required for DeepSeek provider.")

    return ChatDeepSeek(
        model=DEEPSEEK_MODEL,
        temperature=temperature,
        api_key=DEEPSEEK_API_KEY,
        **kwargs,
    )

def _build_model_by_provider(
    provider: str,
    temperature: float = DEFAULT_TEMPERATURE,
    **kwargs: Any,
) -> BaseChatModel:
    validated_provider = validate_llm_provider(provider)

    if validated_provider == "openai":
        return _build_openai_model(
            temperature=temperature,
            **kwargs,
        )

    if validated_provider == "xai":
        return _build_xai_model(
            temperature=temperature,
            **kwargs,
        )

    if validated_provider == "deepseek":
        return _build_deepseek_model(
            temperature=temperature,
            **kwargs,
        )

    raise LLMProviderError(f"Unsupported provider: {provider}")

def get_chat_model(
    provider: str | None = None,
    temperature: float = DEFAULT_TEMPERATURE,
    use_fallback: bool = True,
    **kwargs: Any,
) -> BaseChatModel:
    selected_provider = provider or LLM_PROVIDER

    try:
        return _build_model_by_provider(
            provider = selected_provider,
            temperature= temperature,
            **kwargs
        )
    except Exception as primary_error:
        if not use_fallback:
            raise LLMProviderError(
                f"Failed to initialize provider '{selected_provider}'. "
                f"Error: {primary_error}"
            ) from primary_error
        
        fallback_provider = validate_llm_provider(LLM_FALLBACK_PROVIDER)

        if fallback_provider == selected_provider:
           raise LLMProviderError(
                f"Failed to initialize provider '{selected_provider}' and fallback "
                f"provider is the same. Error: {primary_error}"
            ) from primary_error
        
        try:
            return _build_model_by_provider(
                provider=fallback_provider,
                temperature= temperature,
                **kwargs,
            )
        
        except Exception as fallback_error:
            raise LLMProviderError(
                f"Failed to initialize provider '{selected_provider}' and fallback "
                f"provider '{fallback_provider}'. "
                f"Primary error: {primary_error}. "
                f"Fallback error: {fallback_error}"
            ) from fallback_error
            
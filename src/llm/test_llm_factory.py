from src.config.settings import LLM_PROVIDER
from src.llm.llm_factory import get_chat_model


def test_provider_factory() -> None:
    print("=" * 80)
    print("Testing LLM Provider Factory")
    print(f"Configured provider: {LLM_PROVIDER}")

    model = get_chat_model()

    response = model.invoke(
        "Reply with exactly this sentence: Provider factory is working."
    )

    print("Model class:", model.__class__.__name__)
    print("Response:")
    print(response.content)
    print("=" * 80)


if __name__ == "__main__":
    test_provider_factory()
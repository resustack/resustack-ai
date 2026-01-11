from langchain_anthropic import ChatAnthropic

from backend.ai.config import get_ai_config


def get_anthropic_client() -> ChatAnthropic:
    """Anthropic Claude 클라이언트 생성."""
    config = get_ai_config()

    client = ChatAnthropic(
        model=config.anthropic_model,
        anthropic_api_key=config.anthropic_api_key,
        max_tokens=config.anthropic_max_tokens,
        temperature=config.anthropic_temperature,
        # top_p=config.anthropic_top_p,
    )
    return client

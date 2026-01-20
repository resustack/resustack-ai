from functools import lru_cache

from anthropic import APIConnectionError, APITimeoutError, RateLimitError
from langchain_anthropic import ChatAnthropic

from backend.ai.config import get_ai_config


@lru_cache
def get_anthropic_client() -> ChatAnthropic:
    """Anthropic Claude 클라이언트 싱글톤 반환."""
    config = get_ai_config()

    client = ChatAnthropic(
        model=config.anthropic_model,
        anthropic_api_key=config.anthropic_api_key,
        max_tokens=config.anthropic_max_tokens,
        temperature=config.anthropic_temperature,
        default_request_timeout=90.0,
    )

    return client.with_retry(
        retry_if_exception_type=(
            APIConnectionError,
            APITimeoutError,
            RateLimitError,
        ),
        stop_after_attempt=3,
        wait_exponential_jitter=True,
        exponential_jitter_params={
            "initial": 4,
            "max": 10,
        },
    )

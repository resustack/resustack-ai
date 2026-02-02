from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_project_root() -> Path:
    """프로젝트 루트 디렉토리 경로 반환."""
    current_file = Path(__file__)
    # backend/ai/config.py -> backend/ai -> backend -> project root
    return current_file.parent.parent.parent


class AIConfig(BaseSettings):
    """AI 서비스 설정 클래스."""

    model_config = SettingsConfigDict(
        env_file=str(_get_project_root() / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Anthropic API 설정
    anthropic_api_key: str = Field(
        ...,
        description="Anthropic API 키",
    )
    anthropic_model: str = Field(
        default="claude-haiku-4-5-20251001",
        description="사용할 Anthropic 모델명",
    )
    anthropic_max_tokens: int = Field(
        default=4096,
        description="최대 생성 토큰 수",
        ge=1,
        le=8192,
    )
    anthropic_temperature: float = Field(
        default=0.7,
        description="응답 생성 온도 (0.0 ~ 1.0)",
        ge=0.0,
        le=1.0,
    )
    anthropic_top_p: float = Field(
        default=0.9,
        description="nucleus sampling 값",
        ge=0.0,
        le=1.0,
    )


@lru_cache
def get_ai_config() -> AIConfig:
    """AI 설정 싱글톤 인스턴스 반환."""
    return AIConfig()

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_project_root() -> Path:
    """프로젝트 루트 디렉토리 경로 반환."""
    current_file = Path(__file__)
    # backend/api/rest/config.py -> backend/api/rest -> backend/api -> backend -> project root
    return current_file.parent.parent.parent.parent


class APIConfig(BaseSettings):
    """API 서버 설정 클래스.

    환경변수 우선순위:
    1. 시스템 환경변수 (최우선)
    2. .env 파일
    3. 기본값
    """

    model_config = SettingsConfigDict(
        env_file=str(_get_project_root() / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 서버 설정
    app_host: str = Field(
        default="0.0.0.0",
        description="서버 호스트",
    )
    app_port: int = Field(
        default=8000,
        description="서버 포트",
        ge=1,
        le=65535,
    )
    env: str = Field(
        default="dev",
        description="실행 환경 (dev, prod)",
    )

    # CORS 설정
    allowed_origins: str = Field(
        default="http://localhost:3000",
        description="CORS 허용 도메인 (쉼표로 구분)",
    )

    # Rate limiting 설정
    rate_limit_enabled: bool = Field(
        default=True,
        description="Rate limiting 활성화 여부",
    )
    rate_limit_requests: int = Field(
        default=100,
        description="시간당 요청 제한 수 (requests per hour)",
    )
    rate_limit_reviews_per_hour: int = Field(
        default=10,
        description="시간당 리뷰 API 요청 제한 수",
    )
    rate_limit_skip_paths: str = Field(
        default="/health,/",
        description="Rate limiting을 적용하지 않을 경로 (쉼표로 구분)",
    )

    @property
    def cors_origins(self) -> list[str]:
        """CORS 허용 도메인 리스트 반환."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def rate_limit_skip_paths_list(self) -> list[str]:
        """Rate limiting 제외 경로 리스트 반환."""
        return [path.strip() for path in self.rate_limit_skip_paths.split(",")]

    @property
    def is_dev(self) -> bool:
        """개발 환경 여부."""
        return self.env == "dev"


@lru_cache
def get_api_config() -> APIConfig:
    """API 설정 싱글톤 인스턴스 반환."""
    return APIConfig()

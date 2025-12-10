"""Application configuration using Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: str = Field(default="development", description="Environment name")
    log_level: str = Field(default="INFO", description="Logging level")

    # Anthropic API
    anthropic_api_key: str = Field(..., description="Anthropic API key")

    # External Services
    core_service_url: str = Field(default="http://localhost:8000", description="Core service URL")
    gateway_url: str = Field(default="http://localhost:8080", description="Gateway URL")

    # Security
    jwt_secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_access_token_expire_minutes: int = Field(
        default=30, description="JWT access token expiration in minutes"
    )

    # CORS
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080",
        description="Comma-separated allowed origins",
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()

"""
Configuration management for Deep Agent application.
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Database Configuration
    database_url: str = Field(env="DATABASE_URL")
    postgres_user: str = Field(env="POSTGRES_USER")
    postgres_password: str = Field(env="POSTGRES_PASSWORD")
    postgres_db: str = Field(env="POSTGRES_DB")

    # Redis Configuration
    redis_url: str = Field(env="REDIS_URL")
    redis_password: Optional[str] = Field(env="REDIS_PASSWORD", default=None)

    # API Keys
    openai_api_key: str = Field(env="OPENAI_API_KEY")
    anthropic_api_key: str = Field(env="ANTHROPIC_API_KEY")
    pinecone_api_key: Optional[str] = Field(env="PINECONE_API_KEY", default=None)
    pinecone_environment: Optional[str] = Field(env="PINECONE_ENVIRONMENT", default=None)

    # JWT Configuration
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(env="ALGORITHM", default="HS256")
    access_token_expire_minutes: int = Field(env="ACCESS_TOKEN_EXPIRE_MINUTES", default=30)

    # Application Configuration
    environment: str = Field(env="ENVIRONMENT", default="development")
    debug: bool = Field(env="DEBUG", default=False)
    host: str = Field(env="HOST", default="0.0.0.0")
    port: int = Field(env="PORT", default=8000)
    frontend_url: str = Field(env="FRONTEND_URL", default="http://localhost:3000")

    # External API Keys
    google_api_key: Optional[str] = Field(env="GOOGLE_API_KEY", default=None)
    github_token: Optional[str] = Field(env="GITHUB_TOKEN", default=None)

    # File Upload
    upload_dir: str = Field(env="UPLOAD_DIR", default="uploads")
    max_file_size: int = Field(env="MAX_FILE_SIZE", default=10485760)  # 10MB

    # Rate Limiting
    rate_limit_requests: int = Field(env="RATE_LIMIT_REQUESTS", default=100)
    rate_limit_window: int = Field(env="RATE_LIMIT_WINDOW", default=60)

    # Security
    cors_origins: List[str] = Field(
        env="CORS_ORIGINS",
        default=["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def database_settings(self) -> dict:
        """Get database connection settings."""
        return {
            "url": self.database_url,
            "echo": self.is_development,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
        }

    @property
    def redis_settings(self) -> dict:
        """Get Redis connection settings."""
        return {
            "host": "localhost",
            "port": 6379,
            "password": self.redis_password,
            "decode_responses": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        }


# Global settings instance
settings = Settings()
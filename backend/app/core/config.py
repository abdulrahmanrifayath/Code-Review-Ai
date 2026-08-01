from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "ReviewAI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Security & Tokens
    SECRET_KEY: str = "super-secret-key-change-in-production-min-32-chars"
    ENCRYPTION_KEY: str = "gAAAAABl-z8V5wN6jM_0vF9h4Z5X8yK3m2P7Q1R0S9T8U7V6W5X4Y3Z2A1B0C=" # Fernet 32-byte urlsafe base64
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # Database
    POSTGRES_USER: str = "reviewai"
    POSTGRES_PASSWORD: str = "reviewai_pass"
    POSTGRES_DB: str = "reviewai_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql+asyncpg://reviewai:reviewai_pass@localhost:5432/reviewai_db"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

    # GitHub OAuth & Webhooks
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:5173/oauth/callback"
    GITHUB_WEBHOOK_SECRET: str = ""

    # AI & LLM Provider Settings
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

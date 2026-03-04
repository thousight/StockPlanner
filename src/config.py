from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API configuration
    PROJECT_NAME: str = "StockPlanner API"
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Database configuration
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/stockplanner"
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CHECKPOINT_TTL_MIN: int = 30
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Ensures the database URL uses the asyncpg driver."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url
    
    # Security & Third-party APIs
    OPENAI_API_KEY: Optional[str] = None
    
    # JWT configuration
    JWT_SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10
    
    # CORS configuration
    CORS_ORIGINS: list[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

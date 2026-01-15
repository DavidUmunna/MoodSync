"""
Application configuration settings.
This file should be in: app/core/config.py

Loads configuration from environment variables with sensible defaults.
"""
import os
from typing import Any
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "MoodSync"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("NODE_ENV", "development")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://moodsyncAdmin:Halden101@localhost:5432/moodsync"
    )
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD")
    
    # JWT / Security
    SECRET_KEY: str = os.getenv("JWT_SECRET", "change-me-in-production")
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "14"))
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8000",  # FastAPI docs
    ]
    
    # Rate Limiting
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "1800"))  # 30 minutes
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    def get_redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


# Create a global settings instance
settings = Settings()


# Validate critical settings on startup
def validate_settings():
    """Validate critical configuration settings."""
    errors = []
    
    if settings.SECRET_KEY == "change-me-in-production" and settings.ENVIRONMENT == "production":
        errors.append("❌ SECRET_KEY must be changed in production!")
    
    if not settings.DATABASE_URL:
        errors.append("❌ DATABASE_URL is not set!")
    
    if "postgresql" not in settings.DATABASE_URL:
        errors.append("⚠️  DATABASE_URL should use PostgreSQL")
    
    if errors:
        print("\n" + "="*60)
        print("⚠️  Configuration Warnings:")
        for error in errors:
            print(f"  {error}")
        print("="*60 + "\n")
        
        if settings.ENVIRONMENT == "production":
            raise ValueError("Critical configuration errors in production!")
    
    # Print configuration summary
    print("\n" + "="*60)
    print(f"🚀 {settings.APP_NAME} Configuration")
    print("="*60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug: {settings.DEBUG}")
    print(f"Database: {settings.DATABASE_URL.split('@')[-1]}")  # Hide credentials
    print(f"Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    print(f"Access Token TTL: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print(f"Refresh Token TTL: {settings.REFRESH_TOKEN_EXPIRE_DAYS} days")
    print("="*60 + "\n")


# Run validation when module is imported
validate_settings()
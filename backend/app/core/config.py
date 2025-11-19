"""
Core Configuration Module
~~~~~~~~~~~~~~~~~~~~~~~~~~

Manages application configuration using Pydantic Settings.
Loads environment variables and provides type-safe configuration access.
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings can be overridden via .env file or environment variables.
    """
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./employees.db",
        description="Database connection URL"
    )
    
    # LLM Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(
        default="gpt-4-turbo-preview",
        description="OpenAI model to use"
    )
    
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    anthropic_model: str = Field(
        default="claude-3-sonnet-20240229",
        description="Anthropic model to use"
    )
    
    llm_provider: str = Field(
        default="openai",
        description="LLM provider: openai, anthropic, or local"
    )
    
    # Application Configuration
    app_name: str = Field(
        default="CyberSecurity Training Assistant",
        description="Application name"
    )
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Security Configuration
    secret_key: str = Field(
        default="change-this-secret-key-in-production",
        description="Secret key for JWT encoding"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=60,
        description="Access token expiration time in minutes"
    )
    
    # CORS Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins"
    )
    
    # Session Configuration
    session_timeout_minutes: int = Field(
        default=30,
        description="Session timeout in minutes"
    )
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


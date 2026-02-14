"""Application configuration using environment variables."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Data directory path
    data_path: Path = Path("data")
    
    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Application
    app_name: str = "Kayakish - Hull Analysis Tool"
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
settings = Settings()

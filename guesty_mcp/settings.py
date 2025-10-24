"""Settings and configuration for the Guesty MCP server."""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # HTTP Client settings
    request_timeout_s: int = 30
    max_retries: int = 3
    
    # Logging settings
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "GUESTY_MCP_"
        case_sensitive = False


settings = Settings()

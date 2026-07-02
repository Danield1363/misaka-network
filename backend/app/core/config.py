from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    PROJECT_NAME: str = "Misaka Core"
    VERSION: str = "0.1 Genesis"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    API_PREFIX: str = "/api"
    
    LOG_LEVEL: str = "INFO"
    
    LLM_PROVIDER: str = "mock"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-pro"
    
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    MEMORY_ENABLED: bool = False
    NOTIFICATIONS_ENABLED: bool = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
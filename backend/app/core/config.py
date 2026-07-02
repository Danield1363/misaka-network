from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Misaka Core"
    VERSION: str = "0.3 Genesis"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    API_PREFIX: str = "/api"

    LOG_LEVEL: str = "INFO"

    LLM_PROVIDER: str = "mock"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-pro"
    GEMINI_FALLBACK_MODEL: str = "gemini-2.5-flash"
    GEMINI_SECONDARY_FALLBACK_MODEL: str = "gemini-2.5-flash-lite"
    GEMINI_MAX_CONTEXT_CHARS: int = 12000
    GEMINI_MAX_OUTPUT_TOKENS: int = 1024
    GEMINI_RATE_LIMIT_COOLDOWN_SECONDS: int = 60

    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    MEMORY_ENABLED: bool = False
    NOTIFICATIONS_ENABLED: bool = False
    NOTIFICATION_INGEST_TOKEN: str = ""

    ANDROID_BRIDGE_ENABLED: bool = False
    DESKTOP_CONTROL_ENABLED: bool = True
    WAKE_WORD_ENABLED: bool = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

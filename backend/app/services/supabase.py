import logging
from typing import Any
from app.core.config import get_settings

logger = logging.getLogger(__name__)

_client: Any = None


def get_supabase_client() -> Any:
    global _client
    
    settings = get_settings()
    
    if not settings.MEMORY_ENABLED:
        return None
    
    if _client is not None:
        return _client
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        logger.warning("Supabase not configured, memory disabled")
        return None
    
    try:
        from supabase import create_client
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        logger.info("Supabase client created")
        return _client
    except ImportError:
        logger.error("supabase package not installed")
        return None
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None


def is_memory_enabled() -> bool:
    settings = get_settings()
    return settings.MEMORY_ENABLED and get_supabase_client() is not None
import logging
import sys
from typing import Optional


def setup_logging(log_level: Optional[str] = None) -> None:
    from app.core.config import get_settings
    
    settings = get_settings()
    level = log_level or settings.LOG_LEVEL
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {level} level")
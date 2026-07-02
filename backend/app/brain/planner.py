import logging

logger = logging.getLogger(__name__)


class Planner:
    def detect_intent(self, message: str) -> str:
        logger.info(f"Detecting intent for: {message[:50]}...")
        return "conversation"
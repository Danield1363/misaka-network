import logging
from typing import Any
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class GeminiProvider:
    name: str = "gemini"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None

    async def _get_client(self) -> Any:
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.settings.GEMINI_API_KEY)
                self._client = genai.GenerativeModel(self.settings.GEMINI_MODEL)
            except ImportError:
                logger.error("google-generativeai not installed")
                raise
        return self._client

    async def generate(self, message: str, context: dict[str, Any]) -> str:
        logger.info(f"GeminiProvider generating response for: {message[:50]}...")
        
        try:
            client = await self._get_client()
            personality = context.get("personality", "")
            
            prompt = f"{personality}\n\nUsuário: {message}\nMisaka:"
            
            response = client.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise

    def is_available(self) -> bool:
        return bool(self.settings.GEMINI_API_KEY)
import logging
from typing import Any
from app.core.config import get_settings
from app.llm.errors import ProviderNotFoundError, ProviderUnavailableError
from app.llm.providers.mock import MockProvider
from app.llm.providers.gemini import GeminiProvider

logger = logging.getLogger(__name__)


class LLMGateway:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.providers: dict[str, Any] = {
            "mock": MockProvider(),
            "gemini": GeminiProvider()
        }
        self.default_provider = self.settings.LLM_PROVIDER

    def get_provider(self, provider_name: str | None = None) -> Any:
        name = provider_name or self.default_provider
        provider = self.providers.get(name)
        
        if provider is None:
            raise ProviderNotFoundError(f"Provider '{name}' not found")
        
        if not provider.is_available():
            raise ProviderUnavailableError(
                f"Provider '{name}' is configured but not available. "
                f"Check if the API key is set correctly."
            )
        
        return provider

    async def generate(
        self,
        message: str,
        context: dict[str, Any],
        provider_name: str | None = None
    ) -> dict[str, Any]:
        provider = self.get_provider(provider_name)
        
        logger.info(f"Generating with provider: {provider.name}")
        
        response = await provider.generate(message, context)
        
        return {
            "response": response,
            "provider": provider.name,
            "model": None if provider.name == "mock" else self.settings.GEMINI_MODEL
        }
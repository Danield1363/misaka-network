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
        self.gemini_provider = GeminiProvider()
        self.mock_provider = MockProvider()
        self.providers: dict[str, Any] = {
            "mock": self.mock_provider,
            "gemini": self.gemini_provider,
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

        result = {
            "response": response,
            "provider": provider.name,
            "model": None if provider.name == "mock" else self.settings.GEMINI_MODEL
        }

        if provider.name == "gemini":
            status = self.gemini_provider.get_status()
            result["model_used"] = status.get("active_model")
            result["fallback_used"] = status.get("fallback_used")
            result["last_error_type"] = status.get("last_error_type")

        return result

    def get_llm_status(self) -> dict[str, Any]:
        if self.settings.LLM_PROVIDER == "gemini":
            return self.gemini_provider.get_status()
        return {
            "provider": "mock",
            "primary_model": "mock",
            "fallback_model": "",
            "secondary_fallback_model": "",
            "active_model": "mock",
            "gemini_configured": False,
            "ready": True,
            "last_error_type": "",
            "fallback_used": "",
            "cooldowns": {}
        }

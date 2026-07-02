import logging
import time
from typing import Any
from app.core.config import get_settings
from app.llm.errors import (
    QuotaExceededError, RateLimitError, ModelNotFoundError, GenerationError
)

logger = logging.getLogger(__name__)


class GeminiProvider:
    name: str = "gemini"

    def __init__(self) -> None:
        self.settings = get_settings()
        self._clients: dict[str, Any] = {}
        self._cooldowns: dict[str, float] = {}
        self._last_error_type: str | None = None
        self._fallback_used: str | None = None
        self._active_model: str = self.settings.GEMINI_MODEL

    def _is_cooling_down(self, model: str) -> bool:
        if model in self._cooldowns:
            elapsed = time.time() - self._cooldowns[model]
            if elapsed < self.settings.GEMINI_RATE_LIMIT_COOLDOWN_SECONDS:
                return True
            del self._cooldowns[model]
        return False

    def _set_cooldown(self, model: str) -> None:
        self._cooldowns[model] = time.time()
        logger.warning(f"Cooldown set for model {model} ({self.settings.GEMINI_RATE_LIMIT_COOLDOWN_SECONDS}s)")

    async def _get_client(self, model: str | None = None) -> Any:
        model = model or self.settings.GEMINI_MODEL
        if model not in self._clients:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.settings.GEMINI_API_KEY)
                self._clients[model] = genai.GenerativeModel(model)
            except ImportError:
                logger.error("google-generativeai not installed")
                raise
        return self._clients[model]

    def _detect_error_type(self, error: Exception) -> str:
        error_str = str(error).lower()
        if "429" in error_str or "rate" in error_str:
            return "rate_limit"
        if "resource_exhausted" in error_str or "quota" in error_str:
            return "quota_exceeded"
        if "daily" in error_str and ("limit" in error_str or "exceeded" in error_str):
            return "daily_limit"
        if "api key" in error_str or "invalid" in error_str and "key" in error_str:
            return "invalid_api_key"
        if "not found" in error_str or "model" in error_str:
            return "model_not_found"
        if "network" in error_str or "connection" in error_str or "timeout" in error_str:
            return "network_error"
        return "unknown"

    def _is_quota_error(self, error_type: str) -> bool:
        return error_type in ("rate_limit", "quota_exceeded", "daily_limit")

    async def generate(self, message: str, context: dict[str, Any]) -> str:
        models_to_try = [
            self.settings.GEMINI_MODEL,
            self.settings.GEMINI_FALLBACK_MODEL,
            self.settings.GEMINI_SECONDARY_FALLBACK_MODEL,
        ]

        last_error = None
        for model in models_to_try:
            if self._is_cooling_down(model):
                logger.info(f"Model {model} is cooling down, skipping")
                continue

            try:
                client = await self._get_client(model)
                personality = context.get("personality", "")
                memory_context = context.get("memory_context", "")

                prompt_parts = []
                if personality:
                    prompt_parts.append(personality[:3000])
                if memory_context:
                    prompt_parts.append(memory_context[:2000])
                prompt_parts.append(f"Usuário: {message}")
                prompt_parts.append("Misaka:")

                prompt = "\n\n".join(prompt_parts)

                response = client.generate_content(prompt)
                self._active_model = model
                self._last_error_type = None
                self._fallback_used = model if model != self.settings.GEMINI_MODEL else None
                return response.text

            except Exception as e:
                error_type = self._detect_error_type(e)
                self._last_error_type = error_type
                last_error = e
                logger.warning(f"Gemini error with model {model}: {error_type} - {e}")

                if self._is_quota_error(error_type):
                    self._set_cooldown(model)
                    continue
                elif error_type == "model_not_found":
                    continue
                elif error_type == "invalid_api_key":
                    raise
                else:
                    raise

        if last_error:
            error_type = self._detect_error_type(last_error)
            if self._is_quota_error(error_type):
                self._fallback_used = "all_models_exhausted"
                raise QuotaExceededError(
                    model="all",
                    error_type=error_type
                )
            raise GenerationError(f"Gemini generation failed: {last_error}")

        raise GenerationError("All Gemini models are cooling down")

    def get_status(self) -> dict[str, Any]:
        return {
            "provider": self.name,
            "primary_model": self.settings.GEMINI_MODEL,
            "fallback_model": self.settings.GEMINI_FALLBACK_MODEL,
            "secondary_fallback_model": self.settings.GEMINI_SECONDARY_FALLBACK_MODEL,
            "active_model": self._active_model,
            "gemini_configured": self.is_available(),
            "ready": self.is_available(),
            "last_error_type": self._last_error_type,
            "fallback_used": self._fallback_used,
            "cooldowns": {
                model: int(self.settings.GEMINI_RATE_LIMIT_COOLDOWN_SECONDS - (time.time() - ts))
                for model, ts in self._cooldowns.items()
                if time.time() - ts < self.settings.GEMINI_RATE_LIMIT_COOLDOWN_SECONDS
            }
        }

    def is_available(self) -> bool:
        return bool(self.settings.GEMINI_API_KEY)

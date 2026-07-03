from app.core.config import Settings
from app.voice.errors import VoiceProviderNotConfigured, VoiceError
from app.voice.providers.base import VoiceProvider


class OpenAIVoiceProvider(VoiceProvider):
    name = "openai"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def transcribe(
        self,
        audio_path: str,
        *,
        language: str,
        filename: str,
        content_type: str,
    ) -> dict:
        if not self.settings.OPENAI_API_KEY:
            raise VoiceProviderNotConfigured()

        try:
            from openai import AsyncOpenAI
        except Exception as exc:  # pragma: no cover - optional dependency
            raise VoiceError(
                "Provider OpenAI indisponivel no backend.",
                "openai_dependency_missing",
            ) from exc

        client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model=self.settings.OPENAI_TRANSCRIPTION_MODEL,
                    file=audio_file,
                    language=language or self.settings.VOICE_LANGUAGE,
                )
        except Exception as exc:  # pragma: no cover - external service
            raise VoiceError(
                "Provider de voz falhou. Tente novamente.",
                "voice_provider_failed",
            ) from exc

        return {
            "text": getattr(transcript, "text", "") or "",
            "language": language,
            "confidence": None,
        }


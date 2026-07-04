import os
import tempfile
import time
from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings, get_settings
from app.voice.errors import (
    VoiceError,
    VoiceProviderNotConfigured,
    VoiceValidationError,
)
from app.voice.providers.mock import MockVoiceProvider
from app.voice.providers.openai_provider import OpenAIVoiceProvider
from app.voice.schemas import VoiceStatus, VoiceTranscriptionResponse


ACCEPTED_FORMATS = ["webm", "ogg", "wav", "mp3", "m4a"]
ACCEPTED_CONTENT_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/wav",
    "audio/wave",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/m4a",
    "application/octet-stream",
}


class VoiceService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.last_error: str | None = None

    def status(self) -> VoiceStatus:
        provider_name = self._provider_name()
        ready = self.settings.VOICE_ENABLED and self._is_provider_ready(provider_name)
        provider = provider_name if ready or provider_name in {"mock", "openai"} else "unconfigured"
        return VoiceStatus(
            enabled=self.settings.VOICE_ENABLED,
            provider=provider,
            mode="cloud_voice" if self.settings.VOICE_ENABLED else "unavailable",
            ready=ready,
            max_audio_seconds=self.settings.VOICE_MAX_AUDIO_SECONDS,
            accepted_formats=ACCEPTED_FORMATS,
            last_error=self.last_error,
        )

    async def transcribe_upload(
        self,
        audio: UploadFile | None,
        *,
        language: str | None = None,
        source: str | None = None,
        session_id: str | None = None,
    ) -> VoiceTranscriptionResponse:
        started = time.perf_counter()
        if not self.settings.VOICE_ENABLED:
            raise VoiceProviderNotConfigured()
        if audio is None:
            raise VoiceValidationError("Nenhum audio recebido.", "audio_missing")

        suffix = self._validate_upload_metadata(audio)
        provider = self._get_provider()
        temp_path = ""

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
                temp_path = tmp.name
                size = 0
                while chunk := await audio.read(1024 * 1024):
                    size += len(chunk)
                    if size > self.settings.VOICE_MAX_AUDIO_BYTES:
                        raise VoiceValidationError(
                            "Audio muito grande.",
                            "audio_too_large",
                        )
                    tmp.write(chunk)

            if os.path.getsize(temp_path) <= 0:
                raise VoiceValidationError("Nenhum audio recebido.", "audio_empty")

            result = await provider.transcribe(
                temp_path,
                language=language or self.settings.VOICE_LANGUAGE,
                filename=audio.filename or f"audio.{suffix}",
                content_type=audio.content_type or "",
                session_id=session_id,
            )
            self.last_error = None
            return VoiceTranscriptionResponse(
                success=True,
                text=(result.get("text") or "").strip(),
                language=result.get("language") or language or self.settings.VOICE_LANGUAGE,
                provider=provider.name,
                duration_ms=round((time.perf_counter() - started) * 1000),
                confidence=result.get("confidence"),
            )
        except VoiceError as exc:
            self.last_error = exc.safe_message
            raise
        except Exception as exc:
            self.last_error = "Provider de voz falhou. Tente novamente."
            raise VoiceError(self.last_error, "voice_provider_failed") from exc
        finally:
            if temp_path:
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            await audio.close()

    def _provider_name(self) -> str:
        return (self.settings.VOICE_PROVIDER or "unconfigured").strip().lower()

    def _is_provider_ready(self, provider_name: str) -> bool:
        if provider_name == "mock":
            return True
        if provider_name == "openai":
            return bool(self.settings.OPENAI_API_KEY)
        return False

    def _get_provider(self):
        provider_name = self._provider_name()
        if provider_name == "mock":
            return MockVoiceProvider(self.settings)
        if provider_name == "openai" and self.settings.OPENAI_API_KEY:
            return OpenAIVoiceProvider(self.settings)
        raise VoiceProviderNotConfigured()

    def _validate_upload_metadata(self, audio: UploadFile) -> str:
        filename = audio.filename or ""
        suffix = Path(filename).suffix.lower().lstrip(".")
        content_type = (audio.content_type or "").split(";")[0].lower()

        if not suffix and content_type == "audio/webm":
            suffix = "webm"
        if not suffix:
            raise VoiceValidationError(
                "Formato de audio nao suportado.",
                "audio_format_unsupported",
            )
        if suffix not in ACCEPTED_FORMATS:
            raise VoiceValidationError(
                "Formato de audio nao suportado.",
                "audio_format_unsupported",
            )
        if content_type and content_type not in ACCEPTED_CONTENT_TYPES:
            raise VoiceValidationError(
                "Formato de audio nao suportado.",
                "audio_format_unsupported",
            )
        return suffix

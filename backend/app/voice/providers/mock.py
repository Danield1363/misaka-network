from app.core.config import Settings
from app.voice.providers.base import VoiceProvider


class MockVoiceProvider(VoiceProvider):
    name = "mock"

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
        return {
            "text": self.settings.VOICE_MOCK_TRANSCRIPT.strip(),
            "language": language,
            "confidence": None,
        }


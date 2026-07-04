from app.core.config import Settings
from app.voice.providers.base import VoiceProvider


_seen_sessions: set[str] = set()


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
        session_id: str | None = None,
    ) -> dict:
        transcript = self.settings.VOICE_MOCK_TRANSCRIPT.strip() or "abrir youtube"
        session_key = (session_id or "").strip()
        if session_key and not self.settings.VOICE_MOCK_REPEAT:
            if session_key in _seen_sessions:
                transcript = ""
            else:
                _seen_sessions.add(session_key)
        return {
            "text": transcript,
            "language": language,
            "confidence": None,
        }

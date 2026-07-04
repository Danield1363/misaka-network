from abc import ABC, abstractmethod


class VoiceProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def transcribe(
        self,
        audio_path: str,
        *,
        language: str,
        filename: str,
        content_type: str,
        session_id: str | None = None,
    ) -> dict:
        raise NotImplementedError

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
    ) -> dict:
        raise NotImplementedError


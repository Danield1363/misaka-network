from pydantic import BaseModel


class VoiceStatus(BaseModel):
    enabled: bool
    provider: str
    mode: str
    ready: bool
    max_audio_seconds: int
    accepted_formats: list[str]
    last_error: str | None = None


class VoiceTranscriptionResponse(BaseModel):
    success: bool
    text: str = ""
    language: str = "pt"
    provider: str = "unconfigured"
    duration_ms: int = 0
    confidence: float | None = None
    error: str | None = None
    safe_message: str | None = None


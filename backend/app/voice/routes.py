from fastapi import APIRouter, File, Form, UploadFile

from app.voice.errors import VoiceError
from app.voice.schemas import VoiceStatus, VoiceTranscriptionResponse
from app.voice.service import VoiceService

router = APIRouter(prefix="/voice", tags=["voice"])


@router.get("/status", response_model=VoiceStatus)
async def voice_status() -> VoiceStatus:
    return VoiceService().status()


@router.post("/transcribe", response_model=VoiceTranscriptionResponse)
async def voice_transcribe(
    audio: UploadFile | None = File(default=None),
    language: str | None = Form(default=None),
    source: str | None = Form(default=None),
    session_id: str | None = Form(default=None),
) -> VoiceTranscriptionResponse:
    try:
        return await VoiceService().transcribe_upload(
            audio,
            language=language,
            source=source,
            session_id=session_id,
        )
    except VoiceError as exc:
        return VoiceTranscriptionResponse(
            success=False,
            provider="unconfigured",
            language=language or "pt",
            error=exc.code,
            safe_message=exc.safe_message,
        )

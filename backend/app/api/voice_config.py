from fastapi import APIRouter

router = APIRouter()


@router.get("/voice-config")
async def voice_config() -> dict[str, str | bool | float]:
    return {
        "voice_enabled": True,
        "auto_speak": False,
        "voice_name": None,
        "speak_suffix_enabled": True,
        "rate": 1.0,
        "pitch": 1.0
    }
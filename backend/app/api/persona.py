from fastapi import APIRouter
from app.persona.engine import PersonaEngine

router = APIRouter()
persona_engine = PersonaEngine()


@router.get("/persona")
async def get_persona() -> dict[str, str | bool | list[str]]:
    return persona_engine.get_profile()
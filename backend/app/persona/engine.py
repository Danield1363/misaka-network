import logging
from app.persona.config import PERSONA
from app.persona.formatter import ResponseFormatter

logger = logging.getLogger(__name__)


class PersonaEngine:
    def __init__(self) -> None:
        self.config = PERSONA
        self.formatter = ResponseFormatter(
            suffix_enabled=self.config.suffix_enabled,
            suffix_text=self.config.suffix_text
        )

    def get_system_prompt(self) -> str:
        return (
            f"Você é {self.config.name}, {self.config.description}. "
            f"Seja {self.config.tone}. "
            f"Ajude Daniel com: {', '.join(self.config.helps_with or [])}."
        )

    def format_response(self, text: str) -> str:
        return self.formatter.format(text)

    def get_profile(self) -> dict[str, str | bool | list[str]]:
        return {
            "name": self.config.name,
            "style": self.config.style,
            "suffix_enabled": self.config.suffix_enabled,
            "suffix_text": self.config.suffix_text,
            "tone": self.config.tone,
            "description": self.config.description,
            "helps_with": self.config.helps_with or []
        }
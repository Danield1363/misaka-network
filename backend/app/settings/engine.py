import logging
from typing import Any
from app.core.config import get_settings

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "voice_enabled": True,
    "auto_speak": False,
    "selected_voice": "",
    "voice_rate": 1.0,
    "voice_pitch": 1.1,
    "speak_suffix_enabled": True,
    "hud_enabled": False,
    "compact_mode": False,
    "desktop_notifications_enabled": False,
    "wake_word_enabled": False,
    "theme": "dark",
    "language": "pt-BR",
}


class SettingsEngine:
    def __init__(self) -> None:
        self.config = get_settings()
        self._settings: dict[str, Any] = dict(DEFAULT_SETTINGS)

    async def get_settings(self) -> dict[str, Any]:
        return dict(self._settings)

    async def update_settings(self, data: dict[str, Any]) -> dict[str, Any]:
        allowed_keys = set(DEFAULT_SETTINGS.keys())
        updated = {}
        for key, value in data.items():
            if key in allowed_keys:
                self._settings[key] = value
                updated[key] = value
            else:
                logger.warning(f"Ignored unknown setting: {key}")
        return updated

    async def reset_settings(self) -> dict[str, Any]:
        self._settings = dict(DEFAULT_SETTINGS)
        return dict(self._settings)

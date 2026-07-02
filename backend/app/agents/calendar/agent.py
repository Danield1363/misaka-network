import logging
from typing import Any
from app.agents.base import BaseAgent
from app.calendar.engine import CalendarEngine
from app.calendar.reminder_engine import ReminderEngine

logger = logging.getLogger(__name__)


class CalendarAgent(BaseAgent):
    name: str = "calendar"
    description: str = "Agent for calendar events and reminders"

    def __init__(self) -> None:
        self.calendar_engine = CalendarEngine()
        self.reminder_engine = ReminderEngine()

    async def run(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"CalendarAgent processing: {message[:50]}...")
        lower_message = message.lower().strip()

        reminder_keywords = ["me lembra", "lembrete", "lembrar", "avisar"]
        is_reminder = any(kw in lower_message for kw in reminder_keywords)

        if is_reminder:
            return await self._handle_reminder(message, context)

        calendar_keywords = ["agenda", "evento", "compromisso", "reunião", "calendário", "hoje"]
        is_calendar = any(kw in lower_message for kw in calendar_keywords)

        if is_calendar:
            return await self._handle_calendar(message, context)

        return {
            "response": "Entendi que isso envolve sua agenda, mas preciso de mais detalhes.",
            "agent": self.name,
            "model": None,
            "metadata": {"intent": "calendar", "mock": True}
        }

    async def _handle_reminder(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "response": "Posso criar esse lembrete, mas preciso de uma data e horário em formato claro.",
            "agent": self.name,
            "model": None,
            "metadata": {"intent": "reminder", "mock": True}
        }

    async def _handle_calendar(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        lower_message = message.lower().strip()

        if "hoje" in lower_message:
            if self.calendar_engine.enabled:
                events = await self.calendar_engine.get_today_events()
                if events:
                    event_list = "\n".join([f"- {e.get('title')} ({e.get('starts_at', '')[:16]})" for e in events])
                    response = f"Seus eventos de hoje:\n{event_list}"
                else:
                    response = "Você não tem eventos para hoje."
            else:
                response = "Agenda não está disponível no momento."
        else:
            if self.calendar_engine.enabled:
                events = await self.calendar_engine.get_upcoming_events()
                if events:
                    event_list = "\n".join([f"- {e.get('title')} ({e.get('starts_at', '')[:16]})" for e in events[:5]])
                    response = f"Próximos eventos:\n{event_list}"
                else:
                    response = "Você não tem eventos próximos."
            else:
                response = "Agenda não está disponível no momento."

        return {
            "response": response,
            "agent": self.name,
            "model": None,
            "metadata": {"intent": "calendar", "mock": True}
        }
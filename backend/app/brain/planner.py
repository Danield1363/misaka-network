import logging

logger = logging.getLogger(__name__)


class Planner:
    def detect_intent(self, message: str) -> str:
        logger.info(f"Detecting intent for: {message[:50]}...")
        lower_message = message.lower().strip()

        # First, check if it's a command handled by CommandRouter
        from app.commands.parser import detect_intent as detect_command_intent
        cmd_match = detect_command_intent(message)
        if cmd_match is not None:
            logger.info(f"Command intent detected: {cmd_match.name}")
            return "command"

        calendar_keywords = ["agenda", "evento", "compromisso", "reunião", "calendário"]
        if any(kw in lower_message for kw in calendar_keywords):
            return "calendar"

        reminder_keywords = ["me lembra", "lembrete", "lembrar", "avisar"]
        if any(kw in lower_message for kw in reminder_keywords):
            return "reminder"

        task_keywords = ["tarefa", "lista de tarefas", "pendência", "concluir tarefa"]
        if any(kw in lower_message for kw in task_keywords):
            return "tasks"

        coding_keywords = ["código", "programa", "bug", "erro", "python", "fastapi"]
        if any(kw in lower_message for kw in coding_keywords):
            return "coding"

        return "conversation"

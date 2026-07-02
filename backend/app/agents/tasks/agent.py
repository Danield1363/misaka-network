import logging
from typing import Any
from app.agents.base import BaseAgent
from app.tools.executor import ToolExecutor

logger = logging.getLogger(__name__)


class TaskAgent(BaseAgent):
    name: str = "tasks"
    description: str = "Agent for task management"

    def __init__(self) -> None:
        self.tool_executor = ToolExecutor()

    async def run(self, message: str, context: dict[str, Any]) -> dict[str, Any]:
        logger.info(f"TaskAgent processing: {message[:50]}...")
        lower_message = message.lower().strip()

        create_keywords = ["cria tarefa", "criar tarefa", "adiciona tarefa", "adicionar tarefa", "nova tarefa"]
        is_create = any(kw in lower_message for kw in create_keywords)

        if is_create:
            title = message
            for kw in create_keywords:
                title = title.replace(kw, "").strip()
            title = title.replace("misaka,", "").replace("misaka", "").strip()
            if not title:
                title = "Nova tarefa"

            result = await self.tool_executor.execute(
                "tasks.create",
                {"title": title, "priority": 3},
                context
            )

            return {
                "response": f"Tarefa criada: {title}" if result.get("success") else "Falha ao criar tarefa.",
                "agent": self.name,
                "model": None,
                "metadata": {
                    "tools_used": ["tasks.create"],
                    "mock": result.get("data", {}).get("status") == "pending"
                }
            }

        list_keywords = ["listar tarefas", "minhas tarefas", "tarefas pendentes", "lista de tarefas"]
        is_list = any(kw in lower_message for kw in list_keywords)

        if is_list:
            result = await self.tool_executor.execute(
                "tasks.list",
                {},
                context
            )

            tasks = result.get("data", {}).get("tasks", [])
            if tasks:
                task_list = "\n".join([f"- {t.get('title')} [{t.get('status')}]" for t in tasks[:5]])
                response = f"Suas tarefas:\n{task_list}"
            else:
                response = "Você não tem tarefas no momento."

            return {
                "response": response,
                "agent": self.name,
                "model": None,
                "metadata": {
                    "tools_used": ["tasks.list"],
                    "mock": True
                }
            }

        return {
            "response": "Entendi que isso envolve tarefas, mas preciso de mais detalhes.",
            "agent": self.name,
            "model": None,
            "metadata": {"tools_used": [], "mock": True}
        }
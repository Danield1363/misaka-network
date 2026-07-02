import logging
from typing import Any
from app.tools.registry import registry
from app.tools.permissions import check_permission
from app.tools.errors import ToolNotFoundError, ToolConfirmationRequiredError, ToolExecutionError
from app.actions.engine import ActionEngine

logger = logging.getLogger(__name__)


class ToolExecutor:
    def __init__(self) -> None:
        self.registry = registry
        self.action_engine = ActionEngine()

    async def execute(
        self,
        tool_name: str,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
        dry_run: bool = False,
        confirmed: bool = False
    ) -> dict[str, Any]:
        try:
            tool = self.registry.get_tool(tool_name)
        except ToolNotFoundError:
            return {
                "success": False,
                "tool": tool_name,
                "error": f"Tool '{tool_name}' not found",
                "metadata": {}
            }

        check_permission(tool, confirmed)

        action_log = await self.action_engine.log_action_start(
            action_name=tool_name,
            tool_name=tool_name,
            input_data=input_data,
            dry_run=dry_run,
            requires_confirmation=tool.requires_confirmation
        )
        action_id = action_log.get("id")

        if dry_run:
            await self.action_engine.log_action_success(
                action_id=action_id,
                output={"dry_run": True},
                metadata={"would_execute": True}
            )
            return {
                "success": True,
                "tool": tool_name,
                "dry_run": True,
                "would_execute": True,
                "input_data": input_data,
                "metadata": {
                    "danger_level": tool.danger_level,
                    "requires_confirmation": tool.requires_confirmation
                }
            }

        try:
            result = await tool.run(input_data, context)
            await self.action_engine.log_action_success(
                action_id=action_id,
                output=result,
                metadata=result.get("metadata", {})
            )
            return {
                "success": True,
                "tool": tool_name,
                "dry_run": False,
                "data": result.get("data", {}),
                "metadata": result.get("metadata", {})
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            await self.action_engine.log_action_error(
                action_id=action_id,
                error=str(e)
            )
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "metadata": {}
            }
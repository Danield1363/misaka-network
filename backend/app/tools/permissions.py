from app.tools.base import ToolBase
from app.tools.errors import ToolPermissionError, ToolConfirmationRequiredError


def check_permission(tool: ToolBase, confirmed: bool) -> None:
    if tool.danger_level in ("medium", "high", "critical"):
        if not tool.requires_confirmation or not confirmed:
            raise ToolConfirmationRequiredError(
                "Esta ação requer confirmação antes de ser executada."
            )
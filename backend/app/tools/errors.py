class ToolError(Exception):
    pass


class ToolNotFoundError(ToolError):
    pass


class ToolExecutionError(ToolError):
    pass


class ToolPermissionError(ToolError):
    pass


class ToolConfirmationRequiredError(ToolError):
    pass
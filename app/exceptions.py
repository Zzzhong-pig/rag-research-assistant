"""应用级异常定义"""


class CopilotError(Exception):
    """Copilot 基础异常"""

    def __init__(self, message: str, code: str = "COPILOT_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class RetrievalError(CopilotError):
    def __init__(self, message: str):
        super().__init__(message, code="RETRIEVAL_ERROR")


class AgentError(CopilotError):
    def __init__(self, message: str):
        super().__init__(message, code="AGENT_ERROR")


class ToolError(CopilotError):
    def __init__(self, message: str):
        super().__init__(message, code="TOOL_ERROR")


class MemoryError(CopilotError):
    def __init__(self, message: str):
        super().__init__(message, code="MEMORY_ERROR")

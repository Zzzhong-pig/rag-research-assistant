"""Tool Calling Framework 基类与注册表"""

from abc import ABC, abstractmethod
from typing import Any

from app.logging_config import setup_logging

logger = setup_logging("copilot.tools")


class BaseTool(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    def run(self, **kwargs) -> dict[str, Any]:
        pass

    def __repr__(self) -> str:
        return f"<Tool:{self.name}>"


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool
        logger.debug("Registered tool: %s", tool.name)

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    def execute(self, name: str, **kwargs) -> dict[str, Any]:
        tool = self.get(name)
        if not tool:
            return {"success": False, "error": f"Unknown tool: {name}"}
        try:
            result = tool.run(**kwargs)
            result.setdefault("success", True)
            result.setdefault("tool", name)
            return result
        except Exception as e:
            logger.exception("Tool %s failed", name)
            return {"success": False, "tool": name, "error": str(e)}


def build_tool_registry() -> ToolRegistry:
    from app.tools.citation import CitationTool
    from app.tools.experiment_design import ExperimentDesignTool
    from app.tools.paper_summary import PaperSummaryTool
    from app.tools.python_analysis import PythonAnalysisTool
    from app.tools.rag_retrieval import RAGRetrievalTool

    registry = ToolRegistry()
    for tool_cls in (
        RAGRetrievalTool,
        PaperSummaryTool,
        ExperimentDesignTool,
        PythonAnalysisTool,
        CitationTool,
    ):
        registry.register(tool_cls())
    return registry

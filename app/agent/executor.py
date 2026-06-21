"""Executor Agent：执行计划步骤，调用工具"""

from langchain_core.documents import Document

from app.logging_config import setup_logging
from app.tools.base import ToolRegistry

logger = setup_logging("copilot.executor")


class ExecutorAgent:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self._docs: list[Document] = []
        self._intermediate: list[str] = []
        self._structured: dict | None = None
        self._tool_results: list[dict] = []

    @property
    def docs(self) -> list[Document]:
        return self._docs

    @property
    def intermediate(self) -> list[str]:
        return self._intermediate

    @property
    def structured(self) -> dict | None:
        return self._structured

    def reset_docs(self, docs: list[Document] | None = None) -> None:
        if docs is not None:
            self._docs = docs

    def execute_step(
        self,
        step: dict,
        question: str,
        intent: str,
        extra_queries: list[str] | None = None,
    ) -> dict:
        tool_name = step.get("tool", "")
        action = step.get("action", "")
        step_query = step.get("query") or question
        logger.info("Executing step %s: %s via %s", step.get("step_id"), action, tool_name)

        if tool_name == "rag_retrieval":
            result = self.registry.execute(
                "rag_retrieval",
                question=step_query,
                task_type=intent.replace("research_analysis", "experiment_design"),
                queries=extra_queries,
            )
            if result.get("success", True) and result.get("docs"):
                self._docs = result["docs"]
            self._tool_results.append(result)
            return result

        if tool_name == "paper_summary":
            result = self.registry.execute(
                "paper_summary", question=question, docs=self._docs
            )
            if result.get("structured"):
                self._structured = result["structured"]
            if result.get("answer"):
                self._intermediate.append(result["answer"])
            self._tool_results.append(result)
            return result

        if tool_name == "experiment_design":
            result = self.registry.execute(
                "experiment_design", question=question, docs=self._docs
            )
            if result.get("structured"):
                self._structured = result["structured"]
            if result.get("answer"):
                self._intermediate.append(result["answer"])
            self._tool_results.append(result)
            return result

        if tool_name == "python_analysis":
            result = self.registry.execute(
                "python_analysis",
                task=step.get("description", question),
                data_description=step_query,
            )
            if result.get("explanation"):
                self._intermediate.append(result["explanation"])
            self._tool_results.append(result)
            return result

        if tool_name == "citation":
            answer = "\n\n".join(self._intermediate)
            result = self.registry.execute(
                "citation", docs=self._docs, answer=answer
            )
            self._tool_results.append(result)
            return result

        return {"success": False, "error": f"Unknown tool in step: {tool_name}"}

    def execute_plan(
        self,
        steps: list[dict],
        question: str,
        intent: str,
        extra_queries: list[str] | None = None,
    ) -> dict:
        for step in steps:
            self.execute_step(step, question, intent, extra_queries)
        return {
            "docs": self._docs,
            "intermediate": self._intermediate,
            "structured": self._structured,
            "tool_results": self._tool_results,
        }

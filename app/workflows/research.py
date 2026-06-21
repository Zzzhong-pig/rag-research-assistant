"""Research Analysis Workflow — 综合研究方案"""

from app.agent.reflection import ReflectionEngine
from app.workflows.base import BaseWorkflow


class ResearchWorkflow(BaseWorkflow):
    name = "research_workflow"

    def __init__(self, engine: ReflectionEngine | None = None):
        self.engine = engine or ReflectionEngine()

    def run(self, question: str, memory_context: str = "") -> dict:
        return self.engine.run(
            question=question,
            intent="research_analysis",
            workflow=self.name,
            tools=["rag_retrieval", "paper_summary", "experiment_design", "citation"],
            memory_context=memory_context,
        )

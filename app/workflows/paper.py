"""Paper Summary Workflow"""

from app.agent.reflection import ReflectionEngine
from app.workflows.base import BaseWorkflow


class PaperWorkflow(BaseWorkflow):
    name = "paper_workflow"

    def __init__(self, engine: ReflectionEngine | None = None):
        self.engine = engine or ReflectionEngine()

    def run(self, question: str, memory_context: str = "") -> dict:
        return self.engine.run(
            question=question,
            intent="paper_summary",
            workflow=self.name,
            tools=["rag_retrieval", "paper_summary", "citation"],
            memory_context=memory_context,
        )

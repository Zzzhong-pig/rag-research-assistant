"""QA Workflow"""

from app.agent.reflection import ReflectionEngine
from app.workflows.base import BaseWorkflow


class QAWorkflow(BaseWorkflow):
    name = "qa_workflow"

    def __init__(self, engine: ReflectionEngine | None = None):
        self.engine = engine or ReflectionEngine()

    def run(self, question: str, memory_context: str = "") -> dict:
        return self.engine.run(
            question=question,
            intent="qa",
            workflow=self.name,
            tools=["rag_retrieval", "citation"],
            memory_context=memory_context,
        )

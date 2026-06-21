"""Experiment Design Workflow"""

from app.agent.reflection import ReflectionEngine
from app.workflows.base import BaseWorkflow


class ExperimentWorkflow(BaseWorkflow):
    name = "experiment_workflow"

    def __init__(self, engine: ReflectionEngine | None = None):
        self.engine = engine or ReflectionEngine()

    def run(self, question: str, memory_context: str = "") -> dict:
        return self.engine.run(
            question=question,
            intent="experiment_design",
            workflow=self.name,
            tools=["rag_retrieval", "experiment_design", "citation"],
            memory_context=memory_context,
        )

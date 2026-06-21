"""Workflow 注册与调度"""

from app.workflows.experiment import ExperimentWorkflow
from app.workflows.paper import PaperWorkflow
from app.workflows.qa import QAWorkflow
from app.workflows.research import ResearchWorkflow

WORKFLOW_REGISTRY = {
    "qa_workflow": QAWorkflow,
    "paper_workflow": PaperWorkflow,
    "experiment_workflow": ExperimentWorkflow,
    "research_workflow": ResearchWorkflow,
}


def get_workflow(name: str):
    cls = WORKFLOW_REGISTRY.get(name, QAWorkflow)
    return cls()

"""Tool 3: Experiment Design"""

from app.pipelines.experiment_design import ExperimentDesignPipeline
from app.tools.base import BaseTool


class ExperimentDesignTool(BaseTool):
    name = "experiment_design"
    description = "基于检索片段生成结构化实验设计方案"

    def run(self, question: str, docs=None, **_) -> dict:
        docs = docs or []
        pipeline = ExperimentDesignPipeline()
        result = pipeline.run(question, docs)
        return {
            "answer": result["answer"],
            "structured": result.get("structured"),
            "output_type": "experiment_design",
        }

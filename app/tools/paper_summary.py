"""Tool 2: Paper Summary"""

from app.pipelines.paper_summary import PaperSummaryPipeline
from app.tools.base import BaseTool


class PaperSummaryTool(BaseTool):
    name = "paper_summary"
    description = "基于检索片段生成结构化论文总结（Problem/Method/Dataset/Result/Limitation）"

    def run(self, question: str, docs=None, **_) -> dict:
        docs = docs or []
        pipeline = PaperSummaryPipeline()
        result = pipeline.run(question, docs)
        return {
            "answer": result["answer"],
            "structured": result.get("structured"),
            "output_type": "paper_summary",
        }

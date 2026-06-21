"""Agent Router（Legacy v2 线性编排，保留兼容）

主入口已升级至 app/orchestrator.py → CopilotRouter + ReflectionEngine。
本模块保留供对比测试与渐进迁移。
"""

from app.config import RERANK_TOP_K
from app.pipelines.experiment_design import ExperimentDesignPipeline
from app.pipelines.paper_summary import PaperSummaryPipeline
from app.pipelines.qa import QAPipeline
from app.query.classifier import QueryClassifier
from app.query.expander import MultiQueryExpander
from app.query.rewriter import QueryRewriter
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.reranker import Reranker
from app.utils import format_sources


class AgentRouter:
    PIPELINES = {
        "paper_summary": PaperSummaryPipeline,
        "experiment_design": ExperimentDesignPipeline,
        "qa": QAPipeline,
    }

    def __init__(self):
        self.classifier = QueryClassifier()
        self.rewriter = QueryRewriter()
        self.expander = MultiQueryExpander()
        self.retriever = HybridRetriever()
        self.reranker = Reranker()

    def route(self, question: str) -> dict:
        # Stage 1: Query Understanding
        cls = self.classifier.classify(question)
        task_type = cls["task_type"]
        rewritten = self.rewriter.rewrite(question, task_type)
        queries = self.expander.expand(question, rewritten, task_type)

        # Stage 2: Hybrid Retrieval + Rerank
        candidates = self.retriever.search(queries)
        docs = self.reranker.rerank(rewritten, candidates, RERANK_TOP_K)

        # Stage 3: Pipeline Execution
        pipeline = self.PIPELINES[task_type]()
        result = pipeline.run(question, docs)

        return {
            "answer": result["answer"],
            "structured": result.get("structured"),
            "task_type": task_type,
            "pipeline": f"{task_type}_pipeline",
            "confidence": cls["confidence"],
            "queries": queries,
            "rewritten_query": rewritten,
            "sources": format_sources(docs),
            "retrieval_count": len(candidates),
            "final_count": len(docs),
        }

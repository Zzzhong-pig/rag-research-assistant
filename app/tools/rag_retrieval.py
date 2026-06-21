"""Tool 1: RAG Hybrid Retrieval"""

from langchain_core.documents import Document

from app.config import RERANK_TOP_K
from app.query.expander import MultiQueryExpander
from app.query.rewriter import QueryRewriter
from app.retrieval.hybrid import HybridRetriever
from app.retrieval.reranker import Reranker
from app.tools.base import BaseTool
from app.utils import format_sources


class RAGRetrievalTool(BaseTool):
    name = "rag_retrieval"
    description = "混合检索（FAISS+BM25+RRF+Reranker）获取论文片段"

    def __init__(self):
        self.rewriter = QueryRewriter()
        self.expander = MultiQueryExpander()
        self.retriever = HybridRetriever()
        self.reranker = Reranker()

    def run(
        self,
        question: str,
        task_type: str = "qa",
        queries: list[str] | None = None,
        top_k: int = RERANK_TOP_K,
        **_,
    ) -> dict:
        rewritten = self.rewriter.rewrite(question, task_type)
        search_queries = queries or self.expander.expand(question, rewritten, task_type)
        candidates = self.retriever.search(search_queries)
        docs: list[Document] = self.reranker.rerank(rewritten, candidates, top_k)
        return {
            "docs": docs,
            "sources": format_sources(docs),
            "rewritten_query": rewritten,
            "queries": search_queries,
            "retrieval_count": len(candidates),
            "final_count": len(docs),
        }

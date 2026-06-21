"""Hybrid Retrieval：FAISS + BM25 + RRF 融合排序"""

from langchain_core.documents import Document

from app.config import HYBRID_TOP_K, RRF_K
from app.retrieval.bm25 import BM25Retriever
from app.retrieval.faiss import FAISSRetriever


def _doc_key(doc: Document) -> str:
    return str(doc.metadata.get("chunk_id", hash(doc.page_content)))


class HybridRetriever:
    def __init__(self):
        self.faiss = FAISSRetriever()
        self.bm25 = BM25Retriever()

    def search(self, queries: list[str], top_k: int = HYBRID_TOP_K) -> list[Document]:
        faiss_lists, bm25_lists = [], []
        for q in queries:
            faiss_lists.append(self.faiss.search(q, top_k))
            bm25_lists.append(self.bm25.search(q, top_k))
        return reciprocal_rank_fusion(faiss_lists + bm25_lists, top_k=top_k)


def reciprocal_rank_fusion(
    ranked_lists: list[list[Document]], top_k: int = HYBRID_TOP_K, k: int = RRF_K
) -> list[Document]:
    scores: dict[str, float] = {}
    doc_map: dict[str, Document] = {}

    for results in ranked_lists:
        for rank, doc in enumerate(results):
            key = _doc_key(doc)
            doc_map[key] = doc
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)

    sorted_keys = sorted(scores, key=scores.get, reverse=True)
    return [doc_map[key] for key in sorted_keys[:top_k]]

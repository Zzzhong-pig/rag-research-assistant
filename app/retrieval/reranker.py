"""Cross-Encoder Reranker 重排序"""

from functools import lru_cache

from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from app.config import ENABLE_RERANKER, HF_HUB_OFFLINE, RERANKER_MODEL


@lru_cache(maxsize=1)
def _load_reranker() -> CrossEncoder:
    kwargs = {"local_files_only": True} if HF_HUB_OFFLINE else {}
    return CrossEncoder(RERANKER_MODEL, **kwargs)


class Reranker:
    def rerank(self, query: str, docs: list[Document], top_k: int) -> list[Document]:
        if not ENABLE_RERANKER or not docs:
            return docs[:top_k]

        model = _load_reranker()
        pairs = [[query, d.page_content] for d in docs]
        scores = model.predict(pairs)
        ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in ranked[:top_k]]

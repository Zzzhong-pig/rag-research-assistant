"""BM25 关键词检索"""

import pickle
from functools import lru_cache

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from app.config import BM25_CORPUS_PATH


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


@lru_cache(maxsize=1)
def _load_bm25() -> tuple[BM25Okapi, list[Document]]:
    if not BM25_CORPUS_PATH.exists():
        raise FileNotFoundError(
            f"BM25 语料不存在：{BM25_CORPUS_PATH}，请先运行 python -m app.ingest"
        )
    with open(BM25_CORPUS_PATH, "rb") as f:
        docs: list[Document] = pickle.load(f)
    corpus = [_tokenize(d.page_content) for d in docs]
    return BM25Okapi(corpus), docs


class BM25Retriever:
    def search(self, query: str, top_k: int) -> list[Document]:
        bm25, docs = _load_bm25()
        scores = bm25.get_scores(_tokenize(query))
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)[:top_k]
        return [docs[i] for i, _ in ranked if scores[i] > 0] or [docs[i] for i, _ in ranked]

"""FAISS 向量检索"""

from functools import lru_cache

from langchain_community.vectorstores import FAISS

from app.config import VECTOR_STORE_PATH
from app.llm import get_embeddings


@lru_cache(maxsize=1)
def _load_faiss() -> FAISS:
    if not VECTOR_STORE_PATH.exists():
        raise FileNotFoundError(
            f"向量库不存在：{VECTOR_STORE_PATH}，请先运行 python -m app.ingest"
        )
    embeddings = get_embeddings()
    return FAISS.load_local(
        str(VECTOR_STORE_PATH),
        embeddings,
        allow_dangerous_deserialization=True,
    )


class FAISSRetriever:
    def search(self, query: str, top_k: int) -> list:
        store = _load_faiss()
        return store.similarity_search(query, k=top_k)

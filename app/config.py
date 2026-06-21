import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "papers"
VECTOR_STORE_PATH = Path(os.getenv("VECTOR_STORE_PATH", "./vector_store/faiss_index"))
BM25_CORPUS_PATH = Path(os.getenv("BM25_CORPUS_PATH", "./vector_store/bm25_corpus.pkl"))

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
DOUBAO_MODEL = os.getenv("DOUBAO_MODEL", "deepseek-v4-pro-260425")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
TOP_K = int(os.getenv("TOP_K", "4"))
HYBRID_TOP_K = int(os.getenv("HYBRID_TOP_K", "10"))
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "4"))
RRF_K = int(os.getenv("RRF_K", "60"))
MULTI_QUERY_COUNT = int(os.getenv("MULTI_QUERY_COUNT", "3"))
ENABLE_RERANKER = os.getenv("ENABLE_RERANKER", "true").lower() == "true"

# Agent / Reflection
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "3"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MEMORY_DIR = Path(os.getenv("MEMORY_DIR", "./data/memory"))
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))

# Evaluation
ENABLE_RAGAS = os.getenv("ENABLE_RAGAS", "false").lower() == "true"

# HuggingFace（国内网络可设 HF_ENDPOINT=https://hf-mirror.com）
HF_ENDPOINT = os.getenv("HF_ENDPOINT", "")
HF_HUB_OFFLINE = os.getenv("HF_HUB_OFFLINE", "false").lower() == "true"

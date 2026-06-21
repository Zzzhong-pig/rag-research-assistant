"""豆包 LLM + 本地 HuggingFace Embedding 封装"""

import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI

from app.config import (
    DOUBAO_API_KEY,
    DOUBAO_BASE_URL,
    DOUBAO_MODEL,
    EMBEDDING_MODEL,
    HF_ENDPOINT,
    HF_HUB_OFFLINE,
)

if HF_ENDPOINT:
    os.environ.setdefault("HF_ENDPOINT", HF_ENDPOINT)


def get_llm():
    if not DOUBAO_API_KEY:
        raise ValueError("请先在 .env 中配置 DOUBAO_API_KEY")
    return ChatOpenAI(
        model=DOUBAO_MODEL,
        api_key=DOUBAO_API_KEY,
        base_url=DOUBAO_BASE_URL,
        temperature=0.3,
    )


def get_embeddings():
    embed_kwargs: dict = {"model_name": EMBEDDING_MODEL}
    if HF_HUB_OFFLINE:
        embed_kwargs["model_kwargs"] = {"local_files_only": True}
    return HuggingFaceEmbeddings(**embed_kwargs)

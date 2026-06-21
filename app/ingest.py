"""文档入库：PDF -> 分块 -> FAISS + BM25 语料"""

import pickle
import uuid
from pathlib import Path

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import (
    BM25_CORPUS_PATH,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DATA_DIR,
    VECTOR_STORE_PATH,
)
from app.llm import get_embeddings


def load_and_split_documents(data_dir: Path = DATA_DIR):
    loader = PyPDFDirectoryLoader(str(data_dir))
    documents = loader.load()
    if not documents:
        raise FileNotFoundError(f"未在 {data_dir} 找到 PDF 文件，请先放入科研论文")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    for chunk in chunks:
        chunk.metadata["chunk_id"] = str(uuid.uuid4())
    return chunks


def build_vector_store(data_dir: Path = DATA_DIR, save_path: Path = VECTOR_STORE_PATH):
    chunks = load_and_split_documents(data_dir)
    embeddings = get_embeddings()

    vector_store = FAISS.from_documents(chunks, embeddings)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(save_path))

    with open(BM25_CORPUS_PATH, "wb") as f:
        pickle.dump(chunks, f)

    print(f"入库完成：{len(chunks)} 个文本块")
    print(f"  FAISS -> {save_path}")
    print(f"  BM25  -> {BM25_CORPUS_PATH}")
    return vector_store


if __name__ == "__main__":
    build_vector_store()

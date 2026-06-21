FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV VECTOR_STORE_PATH=/app/vector_store/faiss_index
ENV BM25_CORPUS_PATH=/app/vector_store/bm25_corpus.pkl
ENV MEMORY_DIR=/app/data/memory

EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

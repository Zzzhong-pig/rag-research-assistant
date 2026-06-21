# Agentic RAG 科研知识库 — 架构设计文档

> v2.0 | Agentic RAG | Task-aware | Hybrid Retrieval

---

## 1. Overall Architecture Design

```
用户 Query
    │
    ▼
┌─────────────────────────────────────┐
│     Query Understanding Layer       │
│  Classify → Rewrite → Multi-Expand  │
└─────────────────┬───────────────────┘
                  │ expanded queries
                  ▼
┌─────────────────────────────────────┐
│       Hybrid Retrieval Layer        │
│   FAISS (semantic) + BM25 (keyword) │
│         RRF Fusion Ranking          │
└─────────────────┬───────────────────┘
                  │ Top-N candidates
                  ▼
┌─────────────────────────────────────┐
│          Reranker Module            │
│   Cross-Encoder (bge-reranker-v2)   │
└─────────────────┬───────────────────┘
                  │ Top-K refined docs
                  ▼
┌─────────────────────────────────────┐
│          Agent Router               │
│  paper_summary | experiment | qa    │
└─────────────────┬───────────────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
 PaperSummary  Experiment     QA
 Pipeline      Pipeline    Pipeline
    │             │             │
    └─────────────┼─────────────┘
                  ▼
        Structured Output Generator
                  │
                  ▼
           回答 + 引用来源 + 元数据
```

### 数据流

```
PDF → chunk(500/50) → [FAISS index] + [BM25 corpus.pkl]
Query → LLM classify → LLM rewrite → LLM expand(3 queries)
     → FAISS×N + BM25×N → RRF merge → Rerank Top-4
     → Pipeline(LLM) → JSON/Text output
```

### Agent 决策流程

```
1. classify(question) → task_type + confidence
2. if paper_summary → PaperSummaryPipeline (5-field JSON)
   if experiment_design → ExperimentDesignPipeline (5-field JSON)
   else → QAPipeline (free text)
3. 每个 Pipeline 共享同一套检索结果，但 Prompt 不同 → task-aware RAG
```

---

## 2. Module Breakdown

| 模块 | 文件 | 职责 |
|------|------|------|
| Query Classifier | `app/query/classifier.py` | 三分类路由决策 |
| Query Rewriter | `app/query/rewriter.py` | 检索 query 优化 |
| Multi-Query Expander | `app/query/expander.py` | 一题多 query 扩召回 |
| FAISS Retriever | `app/retrieval/faiss.py` | 语义向量检索 |
| BM25 Retriever | `app/retrieval/bm25.py` | 关键词检索 |
| Hybrid Fusion | `app/retrieval/hybrid.py` | RRF 融合排序 |
| Reranker | `app/retrieval/reranker.py` | Cross-Encoder 精排 |
| Agent Router | `app/agent/router.py` | 全流程编排 |
| Paper Summary | `app/pipelines/paper_summary.py` | 结构化论文总结 |
| Experiment Design | `app/pipelines/experiment_design.py` | 结构化实验方案 |
| QA Pipeline | `app/pipelines/qa.py` | 通用问答 |
| Orchestrator | `app/orchestrator.py` | 对外统一入口 |

---

## 3. Agent Routing Logic

```python
# app/agent/router.py 核心逻辑
cls = classifier.classify(question)        # → task_type
rewritten = rewriter.rewrite(question, task_type)
queries = expander.expand(question, rewritten, task_type)
candidates = hybrid_retriever.search(queries)  # FAISS+BM25+RRF
docs = reranker.rerank(rewritten, candidates, top_k=4)
pipeline = PIPELINES[task_type]()          # 路由到对应 Pipeline
result = pipeline.run(question, docs)
```

路由规则：
- 含「总结/综述/贡献」→ `paper_summary_pipeline`
- 含「实验/方案/设计/训练」→ `experiment_design_pipeline`
- 其他 → `qa_pipeline`
- LLM 分类失败时 fallback 到关键词规则

---

## 4. Retrieval System Upgrade

### 升级前
- 单一 FAISS 向量检索
- Top-4 直接送 LLM

### 升级后
| 阶段 | 技术 | 作用 |
|------|------|------|
| 语义检索 | FAISS + multilingual embedding | 捕捉语义相似 |
| 关键词检索 | BM25Okapi | 精确匹配术语（EEGNet, CBraMod） |
| 融合 | Reciprocal Rank Fusion (k=60) | 合并两路排序 |
| 精排 | bge-reranker-v2-m3 Cross-Encoder | 提升 Top-K 精度 |

### RRF 公式
```
score(d) = Σ 1 / (k + rank_i(d))
```

---

## 5. Pipeline Design

### paper_summary_pipeline
输入：question + reranked docs
输出 JSON：
- Problem / Method / Dataset / Result / Limitation

### experiment_design_pipeline
输入：question + reranked docs
输出 JSON：
- Task Definition / Data Pipeline / Model Design / Training Strategy / Evaluation Metrics

### qa_pipeline
输入：question + reranked docs
输出：自然语言回答 + 引用

---

## 6. Code Structure

```
app/
├── agent/
│   ├── router.py          # Agent 编排器
│   └── prompts.py         # 全部 Prompt 模板
├── query/
│   ├── classifier.py      # Query 分类
│   ├── rewriter.py        # Query 改写
│   └── expander.py        # Multi-Query 扩展
├── retrieval/
│   ├── faiss.py           # 向量检索
│   ├── bm25.py            # 关键词检索
│   ├── hybrid.py          # RRF 融合
│   └── reranker.py        # Cross-Encoder 重排
├── pipelines/
│   ├── base.py            # Pipeline 基类
│   ├── paper_summary.py   # 论文总结
│   ├── experiment_design.py # 实验设计
│   └── qa.py              # 通用问答
├── output/
│   └── formatter.py       # 结构化输出格式化
├── orchestrator.py        # 统一入口 ask()
├── ingest.py              # FAISS + BM25 双索引构建
└── config.py
```

---

## 7. Key Prompt Templates

见 `app/agent/prompts.py`，包含：
- `QUERY_CLASSIFY_PROMPT` — 三分类
- `QUERY_REWRITE_PROMPT` — 检索优化
- `MULTI_QUERY_PROMPT` — 多角度扩展
- `PAPER_SUMMARY_PROMPT` — 5 字段论文总结
- `EXPERIMENT_DESIGN_PROMPT` — 5 字段实验方案
- `QA_SYSTEM_PROMPT` — 通用问答

---

## 快速启动

```powershell
pip install -r requirements.txt
python -m app.ingest          # 构建 FAISS + BM25
streamlit run streamlit_app.py
```

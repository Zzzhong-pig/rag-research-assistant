# Agentic RAG Research Copilot

> v3.0 | LangChain + FAISS + BM25 + DeepSeek | Agent · Planning · Reflection · Tools · Memory · RAGAS

## 项目简介

面向科研论文场景的 **Agentic RAG Research Copilot**：不仅检索论文片段生成回答，还具备完整的 Agent 决策闭环。

系统将 LLM 定位为 **Intent Router / Planner / Critic / Report Writer**，RAG 降级为 Agent 可调用的工具之一，形成：

```
Plan → Execute → Critic → Reflect → Replan → Final Answer
```

### 核心能力

| 能力 | 说明 |
|------|------|
| Hybrid RAG | FAISS + BM25 + RRF + Cross-Encoder Reranker |
| Agent Layer | Router / Planner / Executor / Critic / Writer |
| Reflection Loop | 最多 3 轮自我反思与重检索/重规划 |
| Tool Calling | 5 工具自主调度（RAG / 论文总结 / 实验设计 / Python 分析 / 引用） |
| Memory | 短/长/研究三层记忆 |
| Workflow | QA / Paper / Experiment / Research 四种工作流 |
| Evaluation | RAGAS 可选评估（Faithfulness / Relevancy / Precision） |

## 技术栈

| 模块 | 技术 |
|------|------|
| 文档解析 | PyPDF + LangChain Document Loader |
| 文本分块 | RecursiveCharacterTextSplitter |
| Dense 检索 | FAISS + HuggingFace 多语言 Embedding |
| Sparse 检索 | BM25Okapi |
| 融合排序 | Reciprocal Rank Fusion (RRF) |
| 精排 | bge-reranker-v2-m3 Cross-Encoder |
| 大模型 | DeepSeek-V4-pro（火山方舟） |
| Agent 编排 | Router → Workflow → ReflectionEngine |
| 前端 | Streamlit |
| 后端 API | FastAPI |
| 评估 | RAGAS（可选） |
| 部署 | Docker + docker-compose |

## 项目结构

```
RAG_Project/
├── app/
│   ├── agent/              # Router / Planner / Executor / Critic / Writer / Reflection
│   ├── tools/              # Tool Calling Framework（5 工具）
│   ├── memory/             # Short / Long / Research Memory
│   ├── workflows/          # QA / Paper / Experiment / Research
│   ├── evaluation/         # RAGAS 评估
│   ├── query/              # Query 分类 / 改写 / 扩展
│   ├── retrieval/          # FAISS + BM25 + Hybrid + Reranker
│   ├── pipelines/          # Task-aware Pipeline（Tool 底层）
│   ├── orchestrator.py     # 统一入口 ask()
│   ├── main.py             # FastAPI v3.0
│   ├── ingest.py           # PDF 入库
│   └── config.py           # 环境配置
├── data/papers/            # 科研论文 PDF
├── data/memory/            # 持久化 Memory（运行时生成）
├── vector_store/           # FAISS + BM25 索引
├── docs/
│   └── AGENTIC_COPILOT_ARCHITECTURE.md
├── scripts/
│   ├── demo.py             # 端到端演示（4 类意图）
│   └── cli_query.py        # 命令行问答
├── streamlit_app.py        # Web Copilot 界面
├── Dockerfile
├── docker-compose.yml
├── setup.ps1
└── start.ps1
```

## 快速开始（3 步）

### 1. 获取 API Key 并开通模型

1. 前往 [火山方舟控制台](https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey) 创建 API Key
2. 前往 [模型广场](https://console.volcengine.com/ark/region:ark+cn-beijing/model) **开通**模型（推荐 `deepseek-v4-pro-260425`）

### 2. 安装 + 入库

```powershell
cd f:\RAG_Project
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env   # 填入 DOUBAO_API_KEY
python -m app.ingest     # 构建 FAISS + BM25 双索引
```

或使用一键脚本：

```powershell
.\setup.ps1 -ApiKey "你的API_KEY"
```

### 3. 启动使用

```powershell
# Web Copilot 界面
.\start.ps1

# 或 API 服务
.\start.ps1 -Mode api

# 端到端演示
python scripts\demo.py
```

## 使用方式

### Web 界面

```powershell
streamlit run streamlit_app.py
```

浏览器打开 http://localhost:8501，支持：

- 4 类意图自动路由（问答 / 论文总结 / 实验设计 / 综合研究）
- Agent 决策链路可视化（Plan / Critic / Reflection trace）
- 引用来源与结构化 JSON 输出
- Session 级 Memory

### 命令行

```powershell
python scripts\cli_query.py "RAG的核心思想是什么？"
python scripts\demo.py   # 4 类意图端到端验证
```

### API 接口

```powershell
uvicorn app.main:app --reload
```

```bash
# 问答
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "帮我设计一个EEG情绪识别研究方案", "session_id": "demo-1"}'

# 列出可用工具
curl http://localhost:8000/tools

# 健康检查
curl http://localhost:8000/health
```

### Docker 部署

```powershell
docker-compose up api    # API :8000
docker-compose up ui     # Streamlit :8501
```

## Agent 架构

```
用户 Query
    │
    ▼
CopilotRouter ── intent / workflow / tools
    │
    ▼
Workflow (QA / Paper / Experiment / Research)
    │
    ▼
ReflectionEngine
    Plan → Execute(tools) → Critic → Reflect → Replan
    │
    ▼
Writer → Answer + Structured JSON + Citations
    │
    ▼
MemoryManager (record)
```

### 支持的意图

| 意图 | Workflow | 结构化输出 |
|------|----------|------------|
| qa | qa_workflow | 自然语言 + 引用 |
| paper_summary | paper_workflow | Problem / Method / Dataset / Result / Limitation |
| experiment_design | experiment_workflow | Task / Data / Preprocessing / Model / Training / Evaluation |
| research_analysis | research_workflow | Background / Literature Review / Candidate Methods / Experimental Plan / Risks / Future Work |

## RAGAS 评估（可选）

### 启用步骤

1. 依赖已包含在 `requirements.txt`（`ragas`、`datasets`）

2. 在 `.env` 中开启：

```env
ENABLE_RAGAS=true
```

3. RAGAS 内部 metric 会**复用项目的豆包 LLM**（`DOUBAO_API_KEY`），无需额外配置 OpenAI Key

4. 国内网络建议同时配置 HuggingFace 镜像（Embedding / Reranker 模型下载）：

```env
HF_ENDPOINT=https://hf-mirror.com
```

5. 运行 demo 或 API 查询后，响应中会包含 `evaluation` 字段：

```json
{
  "faithfulness": 0.85,
  "answer_relevancy": 0.92,
  "hallucination_risk": "low"
}
```

> `context_precision` 需要提供 `ground_truth` 才会计算。

## 配置项

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MAX_ITERATIONS` | 3 | Reflection 最大迭代轮数 |
| `HYBRID_TOP_K` | 10 | 混合检索候选数 |
| `RERANK_TOP_K` | 4 | 精排后送 LLM 的文档数 |
| `ENABLE_RERANKER` | true | 是否启用 Cross-Encoder |
| `ENABLE_RAGAS` | false | 是否启用 RAGAS 评估 |
| `HF_ENDPOINT` | （空） | HuggingFace 镜像，国内推荐 `https://hf-mirror.com` |
| `MEMORY_DIR` | ./data/memory | 持久化 Memory 路径 |

完整配置见 [.env.example](.env.example)。

## 内置论文

| 论文 | 说明 |
|------|------|
| Retrieval-Augmented Generation (2020) | RAG 原始论文 |
| Self-RAG (2023) | 自反思 RAG |
| RAG Survey (2024) | RAG 综述 |

可自行添加 PDF 到 `data/papers/`，然后重新运行 `python -m app.ingest`。

## 文档

- [完整架构设计](docs/AGENTIC_COPILOT_ARCHITECTURE.md)
- [Agentic RAG 设计（v2）](docs/AGENTIC_RAG_DESIGN.md)

## License

MIT

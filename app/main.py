"""FastAPI 服务入口 — Agentic RAG Research Copilot"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.config import MAX_ITERATIONS
from app.logging_config import setup_logging
from app.orchestrator import ask

logger = setup_logging("copilot.api")

app = FastAPI(
    title="Agentic RAG Research Copilot",
    version="3.0.0",
    description="Router · Planner · Executor · Critic · Writer · Reflection Loop",
)


class QueryRequest(BaseModel):
    question: str
    session_id: str | None = None


class QueryResponse(BaseModel):
    answer: str
    task_type: str
    intent: str
    workflow: str
    pipeline: str
    structured: dict | None
    sources: list
    tools: list[str]
    confidence: float
    iterations: int
    trace: list
    plan_steps: list
    session_id: str
    evaluation: dict | None = None


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "3.0.0",
        "mode": "agentic_rag_copilot",
        "max_iterations": MAX_ITERATIONS,
    }


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")
    try:
        logger.info("Query received: %s...", req.question[:80])
        result = ask(req.question, session_id=req.session_id)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
def list_tools():
    from app.tools.base import build_tool_registry

    registry = build_tool_registry()
    return {"tools": registry.list_tools()}

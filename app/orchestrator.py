"""Agentic RAG Research Copilot 主入口"""

import uuid
from functools import lru_cache

from app.agent.copilot_router import CopilotRouter
from app.config import ENABLE_RAGAS
from app.logging_config import setup_logging
from app.memory import MemoryManager
from app.workflows import get_workflow

logger = setup_logging("copilot.orchestrator")


@lru_cache(maxsize=1)
def _get_router() -> CopilotRouter:
    return CopilotRouter()


@lru_cache(maxsize=1)
def _get_memory() -> MemoryManager:
    return MemoryManager()


def ask(question: str, session_id: str | None = None) -> dict:
    """Copilot 统一问答入口：Router → Workflow → Reflection Loop → Memory"""
    session_id = session_id or str(uuid.uuid4())
    router = _get_router()
    memory = _get_memory()

    routing = router.route(question)
    intent = routing["intent"]
    workflow_name = routing["workflow"]
    memory_context = memory.research.get_context_for_planner()

    logger.info(
        "Routing: intent=%s workflow=%s confidence=%.2f",
        intent,
        workflow_name,
        routing["confidence"],
    )

    workflow = get_workflow(workflow_name)
    result = workflow.run(question, memory_context)

    memory.record_interaction(
        session_id=session_id,
        question=question,
        answer=result["answer"],
        intent=intent,
        structured=result.get("structured"),
    )

    response = {
        "answer": result["answer"],
        "structured": result.get("structured"),
        "task_type": intent,
        "intent": intent,
        "workflow": workflow_name,
        "pipeline": f"{workflow_name}",
        "tools": routing["tools"],
        "confidence": routing["confidence"],
        "reason": routing["reason"],
        "sources": result.get("sources", []),
        "trace": result.get("trace", []),
        "iterations": result.get("iterations", 1),
        "critic_final": result.get("critic_final"),
        "plan_steps": result.get("plan_steps", []),
        "retrieval_count": result.get("retrieval_count", 0),
        "final_count": result.get("final_count", 0),
        "session_id": session_id,
        "queries": result.get("queries", []),
        "rewritten_query": result.get("rewritten_query", ""),
    }

    if ENABLE_RAGAS:
        try:
            from app.evaluation.ragas_eval import evaluate_response

            response["evaluation"] = evaluate_response(question, response)
        except Exception as e:
            logger.warning("RAGAS evaluation skipped: %s", e)
            response["evaluation"] = {"skipped": True, "reason": str(e)}

    return response



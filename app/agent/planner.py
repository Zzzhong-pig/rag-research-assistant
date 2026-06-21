"""Planner Agent：任务拆解为可执行步骤"""

from app.agent.prompts import PLANNER_AGENT_PROMPT
from app.llm import get_llm
from app.logging_config import setup_logging
from app.utils import parse_llm_json

logger = setup_logging("copilot.planner")

DEFAULT_QA_STEPS = [
    {"step_id": 1, "action": "retrieve", "description": "检索相关论文片段", "tool": "rag_retrieval", "query": ""},
    {"step_id": 2, "action": "write", "description": "生成问答回答", "tool": "citation", "query": ""},
]

DEFAULT_PAPER_STEPS = [
    {"step_id": 1, "action": "retrieve", "description": "检索论文相关内容", "tool": "rag_retrieval", "query": ""},
    {"step_id": 2, "action": "summarize", "description": "结构化论文总结", "tool": "paper_summary", "query": ""},
    {"step_id": 3, "action": "write", "description": "生成引用", "tool": "citation", "query": ""},
]

DEFAULT_EXPERIMENT_STEPS = [
    {"step_id": 1, "action": "retrieve", "description": "检索实验相关文献", "tool": "rag_retrieval", "query": ""},
    {"step_id": 2, "action": "design", "description": "生成实验设计方案", "tool": "experiment_design", "query": ""},
    {"step_id": 3, "action": "write", "description": "生成引用", "tool": "citation", "query": ""},
]

DEFAULT_RESEARCH_STEPS = [
    {"step_id": 1, "action": "retrieve", "description": "检索背景与文献", "tool": "rag_retrieval", "query": ""},
    {"step_id": 2, "action": "retrieve", "description": "检索方法与数据集", "tool": "rag_retrieval", "query": ""},
    {"step_id": 3, "action": "summarize", "description": "综述候选方法", "tool": "paper_summary", "query": ""},
    {"step_id": 4, "action": "design", "description": "设计实验方案", "tool": "experiment_design", "query": ""},
    {"step_id": 5, "action": "write", "description": "撰写研究报告", "tool": "citation", "query": ""},
]

WORKFLOW_DEFAULTS = {
    "qa_workflow": DEFAULT_QA_STEPS,
    "paper_workflow": DEFAULT_PAPER_STEPS,
    "experiment_workflow": DEFAULT_EXPERIMENT_STEPS,
    "research_workflow": DEFAULT_RESEARCH_STEPS,
}


class PlannerAgent:
    def plan(
        self,
        question: str,
        intent: str,
        workflow: str,
        context: str = "",
    ) -> list[dict]:
        llm = get_llm()
        try:
            resp = llm.invoke(
                PLANNER_AGENT_PROMPT.format(
                    intent=intent,
                    workflow=workflow,
                    question=question,
                    context=context or "无",
                )
            )
            data = parse_llm_json(resp.content)
            steps = data.get("steps", [])
            if steps:
                logger.info("Planner generated %d steps for %s", len(steps), workflow)
                return steps
        except Exception as e:
            logger.warning("Planner LLM failed, using defaults: %s", e)

        defaults = WORKFLOW_DEFAULTS.get(workflow, DEFAULT_QA_STEPS)
        return [dict(s) for s in defaults]

"""LLM 驱动的 Router Agent：意图识别 + Workflow 路由"""

from app.agent.prompts import ROUTER_AGENT_PROMPT
from app.llm import get_llm
from app.logging_config import setup_logging
from app.utils import parse_llm_json

logger = setup_logging("copilot.router")

INTENT_WORKFLOW_MAP = {
    "qa": "qa_workflow",
    "paper_summary": "paper_workflow",
    "experiment_design": "experiment_workflow",
    "research_analysis": "research_workflow",
}

INTENT_TOOLS_MAP = {
    "qa": ["rag_retrieval", "citation"],
    "paper_summary": ["rag_retrieval", "paper_summary", "citation"],
    "experiment_design": ["rag_retrieval", "experiment_design", "citation"],
    "research_analysis": ["rag_retrieval", "paper_summary", "experiment_design", "citation"],
}

KEYWORD_RULES = {
    "paper_summary": ["总结", "综述", "介绍", "贡献", "summary", "overview", "这篇论文"],
    "experiment_design": ["实验", "方案", "设计", "pipeline", "训练", "评估", "怎么做", "如何实现"],
    "research_analysis": ["研究方案", "文献调研", "综合", "EEG", "情绪识别", "research plan"],
}


class CopilotRouter:
    def route(self, question: str) -> dict:
        llm = get_llm()
        try:
            resp = llm.invoke(ROUTER_AGENT_PROMPT.format(question=question))
            data = parse_llm_json(resp.content)
            intent = data.get("intent", "qa")
            if intent not in INTENT_WORKFLOW_MAP:
                intent = "qa"
            return {
                "intent": intent,
                "workflow": data.get("workflow") or INTENT_WORKFLOW_MAP[intent],
                "tools": data.get("tools") or INTENT_TOOLS_MAP[intent],
                "confidence": float(data.get("confidence", 0.85)),
                "reason": data.get("reason", "LLM routing"),
            }
        except Exception as e:
            logger.warning("Router LLM failed, rule fallback: %s", e)
            return self._rule_based(question)

    def _rule_based(self, question: str) -> dict:
        q = question.lower()
        scores = {k: 0 for k in INTENT_WORKFLOW_MAP}
        for intent, keywords in KEYWORD_RULES.items():
            for kw in keywords:
                if kw.lower() in q:
                    scores[intent] += 1
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            best = "qa"
        return {
            "intent": best,
            "workflow": INTENT_WORKFLOW_MAP[best],
            "tools": INTENT_TOOLS_MAP[best],
            "confidence": 0.6,
            "reason": "rule-based fallback",
        }

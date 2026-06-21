"""Query Classification：论文总结 / 实验设计 / 问答"""

from app.agent.prompts import QUERY_CLASSIFY_PROMPT
from app.llm import get_llm
from app.utils import parse_llm_json

TASK_TYPES = ("paper_summary", "experiment_design", "qa")

KEYWORD_RULES = {
    "paper_summary": ["总结", "综述", "介绍", "贡献", "summary", "overview", "这篇论文"],
    "experiment_design": ["实验", "方案", "设计", "pipeline", "训练", "评估", "怎么做", "如何实现"],
}


class QueryClassifier:
    def classify(self, question: str) -> dict:
        llm = get_llm()
        try:
            resp = llm.invoke(QUERY_CLASSIFY_PROMPT.format(question=question))
            data = parse_llm_json(resp.content)
            task_type = data.get("task_type", "qa")
            if task_type not in TASK_TYPES:
                task_type = "qa"
            return {
                "task_type": task_type,
                "confidence": float(data.get("confidence", 0.8)),
                "reason": data.get("reason", "LLM classification"),
            }
        except Exception:
            return self._rule_based(question)

    def _rule_based(self, question: str) -> dict:
        q = question.lower()
        scores = {t: 0 for t in TASK_TYPES}
        for task, keywords in KEYWORD_RULES.items():
            for kw in keywords:
                if kw.lower() in q:
                    scores[task] += 1
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            best = "qa"
        return {
            "task_type": best,
            "confidence": 0.6,
            "reason": "rule-based fallback",
        }

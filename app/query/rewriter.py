"""Query Rewriting：优化检索 query"""

from app.agent.prompts import QUERY_REWRITE_PROMPT
from app.llm import get_llm
from app.utils import parse_llm_json


class QueryRewriter:
    def rewrite(self, question: str, task_type: str) -> str:
        llm = get_llm()
        try:
            resp = llm.invoke(
                QUERY_REWRITE_PROMPT.format(question=question, task_type=task_type)
            )
            data = parse_llm_json(resp.content)
            rewritten = data.get("rewritten_query", "").strip()
            return rewritten or question
        except Exception:
            return question

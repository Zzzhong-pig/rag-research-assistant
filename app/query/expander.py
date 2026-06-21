"""Multi-Query Expansion：一题多检索 query"""

from app.agent.prompts import MULTI_QUERY_PROMPT
from app.config import MULTI_QUERY_COUNT
from app.llm import get_llm
from app.utils import parse_llm_json


class MultiQueryExpander:
    def expand(self, question: str, rewritten_query: str, task_type: str) -> list[str]:
        llm = get_llm()
        try:
            resp = llm.invoke(
                MULTI_QUERY_PROMPT.format(
                    count=MULTI_QUERY_COUNT,
                    question=question,
                    rewritten_query=rewritten_query,
                    task_type=task_type,
                )
            )
            data = parse_llm_json(resp.content)
            queries = [q.strip() for q in data.get("queries", []) if q.strip()]
            base = {rewritten_query, question}
            merged = list(base) + [q for q in queries if q not in base]
            return merged[: MULTI_QUERY_COUNT + 2]
        except Exception:
            return list({question, rewritten_query})

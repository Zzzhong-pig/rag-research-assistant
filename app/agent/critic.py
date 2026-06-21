"""Critic Agent：质量评审"""

from app.agent.prompts import CRITIC_AGENT_PROMPT
from app.llm import get_llm
from app.logging_config import setup_logging
from app.utils import parse_llm_json

logger = setup_logging("copilot.critic")


class CriticAgent:
    def evaluate(
        self,
        question: str,
        intent: str,
        answer: str,
        source_count: int,
    ) -> dict:
        llm = get_llm()
        try:
            resp = llm.invoke(
                CRITIC_AGENT_PROMPT.format(
                    question=question,
                    intent=intent,
                    answer=answer[:3000],
                    source_count=source_count,
                )
            )
            result = parse_llm_json(resp.content)
            verdict = result.get("verdict", "PASS")
            if verdict not in ("PASS", "RETRIEVE_AGAIN", "REPLAN"):
                verdict = "PASS"
            result["verdict"] = verdict
            logger.info("Critic verdict: %s", verdict)
            return result
        except Exception as e:
            logger.warning("Critic LLM failed, default PASS: %s", e)
            if source_count == 0:
                return {
                    "verdict": "RETRIEVE_AGAIN",
                    "issues": ["无检索证据"],
                    "missing_evidence": ["需要检索相关论文"],
                    "suggested_queries": [question],
                    "reason": "fallback: no sources",
                }
            return {
                "verdict": "PASS",
                "issues": [],
                "missing_evidence": [],
                "suggested_queries": [],
                "reason": "fallback pass",
            }

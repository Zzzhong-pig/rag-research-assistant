"""Reflection Loop：Plan → Execute → Critic → Reflect → Replan"""

from app.agent.critic import CriticAgent
from app.agent.executor import ExecutorAgent
from app.agent.planner import PlannerAgent
from app.agent.prompts import REFLECT_AGENT_PROMPT
from app.agent.writer import WriterAgent
from app.config import MAX_ITERATIONS
from app.llm import get_llm
from app.logging_config import setup_logging
from app.tools.base import ToolRegistry, build_tool_registry
from app.utils import format_sources, parse_llm_json

logger = setup_logging("copilot.reflection")


class ReflectionEngine:
    """Plan → Execute → Critic → Reflect → Replan 闭环引擎"""

    def __init__(self, registry: ToolRegistry | None = None):
        self.registry = registry or build_tool_registry()
        self.planner = PlannerAgent()
        self.critic = CriticAgent()
        self.writer = WriterAgent()

    def run(
        self,
        question: str,
        intent: str,
        workflow: str,
        tools: list[str],
        memory_context: str = "",
    ) -> dict:
        steps = self.planner.plan(question, intent, workflow, memory_context)
        extra_queries: list[str] = []
        trace: list[dict] = []
        final_executor_result: dict = {}
        critic_result: dict = {"verdict": "PASS"}

        for iteration in range(1, MAX_ITERATIONS + 1):
            logger.info("Reflection iteration %d/%d", iteration, MAX_ITERATIONS)

            executor = ExecutorAgent(self.registry)
            exec_result = executor.execute_plan(steps, question, intent, extra_queries or None)
            final_executor_result = exec_result

            draft_answer = self._draft_answer(exec_result)
            critic_result = self.critic.evaluate(
                question,
                intent,
                draft_answer,
                len(exec_result.get("docs", [])),
            )
            trace.append(
                {
                    "iteration": iteration,
                    "steps": steps,
                    "critic": critic_result,
                    "source_count": len(exec_result.get("docs", [])),
                    "tool_results": exec_result.get("tool_results", []),
                }
            )

            if critic_result["verdict"] == "PASS":
                break

            if iteration >= MAX_ITERATIONS:
                logger.warning("Max iterations reached, proceeding to writer")
                break

            reflection = self._reflect(
                critic_result, iteration, MAX_ITERATIONS
            )
            trace[-1]["reflection"] = reflection

            action = reflection.get("action", "continue")
            if action == "finalize":
                break
            if action == "replan":
                steps = self.planner.plan(
                    question,
                    intent,
                    workflow,
                    memory_context + "\n" + reflection.get("plan_adjustment", ""),
                )
            elif action in ("retrieve_again", "continue"):
                extra_queries = reflection.get("updated_queries") or critic_result.get(
                    "suggested_queries", []
                )
                if critic_result["verdict"] == "RETRIEVE_AGAIN" and not extra_queries:
                    extra_queries = critic_result.get("suggested_queries", [question])

        writer_result = self.writer.write(
            question,
            intent,
            final_executor_result.get("docs", []),
            final_executor_result.get("intermediate", []),
            final_executor_result.get("structured"),
        )

        docs = final_executor_result.get("docs", [])
        sources = format_sources(docs)
        retrieval_meta = self._get_retrieval_meta(final_executor_result)

        return {
            "answer": writer_result["answer"],
            "structured": writer_result.get("structured"),
            "intent": intent,
            "workflow": workflow,
            "tools": tools,
            "sources": sources,
            "trace": trace,
            "iterations": len(trace),
            "critic_final": critic_result,
            "plan_steps": steps,
            "retrieval_count": retrieval_meta["retrieval_count"],
            "final_count": len(docs),
            "queries": retrieval_meta["queries"],
            "rewritten_query": retrieval_meta["rewritten_query"],
        }

    def _draft_answer(self, exec_result: dict) -> str:
        parts = exec_result.get("intermediate", [])
        if parts:
            return "\n\n".join(parts)
        docs = exec_result.get("docs", [])
        if docs:
            return docs[0].page_content[:500]
        return "（暂无回答草稿）"

    def _reflect(self, critic_result: dict, iteration: int, max_iterations: int) -> dict:
        llm = get_llm()
        try:
            resp = llm.invoke(
                REFLECT_AGENT_PROMPT.format(
                    critic_result=str(critic_result),
                    iteration=iteration,
                    max_iterations=max_iterations,
                )
            )
            return parse_llm_json(resp.content)
        except Exception as e:
            logger.warning("Reflect LLM failed: %s", e)
            verdict = critic_result.get("verdict", "PASS")
            if verdict == "REPLAN":
                return {"action": "replan", "reflection": "fallback replan", "updated_queries": []}
            if verdict == "RETRIEVE_AGAIN":
                return {
                    "action": "retrieve_again",
                    "reflection": "fallback retrieve",
                    "updated_queries": critic_result.get("suggested_queries", []),
                }
            return {"action": "continue", "reflection": "fallback continue", "updated_queries": []}

    @staticmethod
    def _get_retrieval_meta(exec_result: dict) -> dict:
        for tr in exec_result.get("tool_results", []):
            if tr.get("retrieval_count") is not None:
                return {
                    "retrieval_count": tr.get("retrieval_count", 0),
                    "queries": tr.get("queries", []),
                    "rewritten_query": tr.get("rewritten_query", ""),
                }
        return {"retrieval_count": 0, "queries": [], "rewritten_query": ""}

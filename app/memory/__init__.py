"""Memory 统一管理"""

from app.config import SESSION_TTL_SECONDS
from app.memory.long_term import LongTermMemory
from app.memory.research import ResearchMemory
from app.memory.short_term import ShortTermMemory


class MemoryManager:
    def __init__(self):
        self.short_term = ShortTermMemory(ttl_seconds=SESSION_TTL_SECONDS)
        self.long_term = LongTermMemory()
        self.research = ResearchMemory()

    def get_session(self, session_id: str):
        return self.short_term.get_session(session_id)

    def record_interaction(
        self,
        session_id: str,
        question: str,
        answer: str,
        intent: str,
        structured: dict | None = None,
    ) -> None:
        session = self.get_session(session_id)
        session.add_message("user", question)
        session.add_message("assistant", answer, intent=intent)

        self.long_term.add_history(session_id, question, answer, {"intent": intent})

        if intent == "paper_summary" and structured:
            title = question[:80]
            self.research.add_paper(title, structured)
        elif intent == "experiment_design" and structured:
            self.research.add_experiment_plan(question[:80], structured)
        elif intent == "research_analysis":
            self.research.add_direction(question[:100])

        self.research.add_task(question, intent, answer)

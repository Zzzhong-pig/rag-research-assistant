"""Research Memory：研究方向、已分析论文、实验方案"""

import json
from pathlib import Path
from typing import Any

from app.config import MEMORY_DIR
from app.logging_config import setup_logging

logger = setup_logging("copilot.research_memory")


class ResearchMemory:
    def __init__(self, storage_dir: Path = MEMORY_DIR):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._file = self.storage_dir / "research.json"
        self._data = self._load()

    def _load(self) -> dict:
        if self._file.exists():
            try:
                return json.loads(self._file.read_text(encoding="utf-8"))
            except Exception:
                logger.warning("Failed to load research memory, starting fresh")
        return {
            "research_directions": [],
            "analyzed_papers": [],
            "experiment_plans": [],
            "task_history": [],
        }

    def _save(self) -> None:
        self._file.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_direction(self, direction: str) -> None:
        dirs = self._data.setdefault("research_directions", [])
        if direction not in dirs:
            dirs.append(direction)
            self._save()

    def add_paper(self, title: str, summary: dict | str) -> None:
        self._data.setdefault("analyzed_papers", []).append(
            {"title": title, "summary": summary}
        )
        if len(self._data["analyzed_papers"]) > 100:
            self._data["analyzed_papers"] = self._data["analyzed_papers"][-100:]
        self._save()

    def add_experiment_plan(self, task: str, plan: dict | str) -> None:
        self._data.setdefault("experiment_plans", []).append(
            {"task": task, "plan": plan}
        )
        self._save()

    def add_task(self, question: str, intent: str, result_summary: str) -> None:
        self._data.setdefault("task_history", []).append(
            {"question": question, "intent": intent, "summary": result_summary[:300]}
        )
        self._save()

    def get_context_for_planner(self) -> str:
        parts = []
        dirs = self._data.get("research_directions", [])
        if dirs:
            parts.append(f"研究方向: {', '.join(dirs[-3:])}")
        papers = self._data.get("analyzed_papers", [])
        if papers:
            titles = [p["title"] for p in papers[-5:]]
            parts.append(f"已分析论文: {', '.join(titles)}")
        return "; ".join(parts) or "无历史研究记忆"

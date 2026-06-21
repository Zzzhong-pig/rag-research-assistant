"""Long-Term Memory：持久化用户偏好与历史"""

import json
from pathlib import Path
from typing import Any

from app.config import MEMORY_DIR
from app.logging_config import setup_logging

logger = setup_logging("copilot.memory")


class LongTermMemory:
    def __init__(self, storage_dir: Path = MEMORY_DIR):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._file = self.storage_dir / "long_term.json"
        self._data = self._load()

    def _load(self) -> dict:
        if self._file.exists():
            try:
                return json.loads(self._file.read_text(encoding="utf-8"))
            except Exception:
                logger.warning("Failed to load long-term memory, starting fresh")
        return {"users": {}, "preferences": {}, "history": []}

    def _save(self) -> None:
        self._file.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def add_history(self, session_id: str, question: str, answer: str, meta: dict | None = None) -> None:
        entry = {
            "session_id": session_id,
            "question": question,
            "answer": answer[:500],
            "meta": meta or {},
        }
        self._data.setdefault("history", []).append(entry)
        if len(self._data["history"]) > 200:
            self._data["history"] = self._data["history"][-200:]
        self._save()

    def set_preference(self, key: str, value: Any) -> None:
        self._data.setdefault("preferences", {})[key] = value
        self._save()

    def get_preference(self, key: str, default=None):
        return self._data.get("preferences", {}).get(key, default)

    def get_history(self, limit: int = 10) -> list[dict]:
        return self._data.get("history", [])[-limit:]

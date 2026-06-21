"""Short-Term Memory：会话级上下文"""

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionMemory:
    session_id: str
    messages: list[dict] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def add_message(self, role: str, content: str, **meta) -> None:
        self.messages.append({"role": role, "content": content, **meta})
        self.updated_at = time.time()

    def get_recent(self, n: int = 5) -> list[dict]:
        return self.messages[-n:]

    def set_context(self, key: str, value: Any) -> None:
        self.context[key] = value
        self.updated_at = time.time()

    def get_context(self, key: str, default=None):
        return self.context.get(key, default)


class ShortTermMemory:
    def __init__(self, ttl_seconds: int = 3600):
        self._sessions: dict[str, SessionMemory] = {}
        self.ttl_seconds = ttl_seconds

    def get_session(self, session_id: str) -> SessionMemory:
        self._cleanup()
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionMemory(session_id=session_id)
        return self._sessions[session_id]

    def _cleanup(self) -> None:
        now = time.time()
        expired = [
            sid
            for sid, s in self._sessions.items()
            if now - s.updated_at > self.ttl_seconds
        ]
        for sid in expired:
            del self._sessions[sid]

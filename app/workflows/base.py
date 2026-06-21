"""Workflow 基类"""

from abc import ABC, abstractmethod


class BaseWorkflow(ABC):
    name: str = ""

    @abstractmethod
    def run(self, question: str, memory_context: str = "") -> dict:
        pass

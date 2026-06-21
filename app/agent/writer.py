"""Writer Agent：整合结果，生成最终输出"""

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from app.agent.prompts import RESEARCH_REPORT_PROMPT, WRITER_AGENT_PROMPT
from app.llm import get_llm
from app.logging_config import setup_logging
from app.utils import parse_llm_json

logger = setup_logging("copilot.writer")

INTENT_TO_OUTPUT = {
    "qa": "qa",
    "paper_summary": "paper_summary",
    "experiment_design": "experiment_design",
    "research_analysis": "research_report",
}


class WriterAgent:
    def write(
        self,
        question: str,
        intent: str,
        docs: list[Document],
        intermediate: list[str],
        structured: dict | None = None,
    ) -> dict:
        output_type = INTENT_TO_OUTPUT.get(intent, "qa")
        context = self._build_context(docs)
        intermediate_text = "\n\n".join(intermediate) if intermediate else "无"

        if structured and output_type in ("paper_summary", "experiment_design"):
            lines = [f"**{k}**: {v}" for k, v in structured.items()]
            return {"answer": "\n\n".join(lines), "structured": structured}

        if output_type == "research_report":
            return self._write_research_report(question, docs, intermediate_text)

        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([("human", WRITER_AGENT_PROMPT)])
        try:
            resp = (prompt | llm).invoke(
                {
                    "question": question,
                    "output_type": output_type,
                    "context": context,
                    "intermediate": intermediate_text,
                }
            )
            content = resp.content.strip()
            if output_type in ("paper_summary", "experiment_design", "research_report"):
                try:
                    structured_out = parse_llm_json(content)
                    lines = [f"**{k}**: {v}" for k, v in structured_out.items()]
                    return {"answer": "\n\n".join(lines), "structured": structured_out}
                except Exception:
                    pass
            return {"answer": content, "structured": structured}
        except Exception as e:
            logger.error("Writer failed: %s", e)
            fallback = intermediate_text or "无法生成回答，请重试。"
            return {"answer": fallback, "structured": structured}

    def _write_research_report(
        self, question: str, docs: list[Document], intermediate: str
    ) -> dict:
        llm = get_llm()
        context = self._build_context(docs)
        prompt = ChatPromptTemplate.from_messages([("human", RESEARCH_REPORT_PROMPT)])
        try:
            resp = (prompt | llm).invoke({"question": question, "context": context})
            structured = parse_llm_json(resp.content)
            lines = [f"**{k}**: {v}" for k, v in structured.items()]
            answer = "\n\n".join(lines)
            if intermediate:
                answer = f"{answer}\n\n---\n\n**中间分析**\n{intermediate}"
            return {"answer": answer, "structured": structured}
        except Exception as e:
            logger.error("Research report failed: %s", e)
            return {"answer": intermediate or "研究报告生成失败", "structured": None}

    @staticmethod
    def _build_context(docs: list[Document]) -> str:
        parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "N/A")
            parts.append(f"[{i}] ({source} p.{page})\n{doc.page_content}")
        return "\n\n".join(parts) if parts else "无检索资料"

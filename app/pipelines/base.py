"""Pipeline 基类"""

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

from app.llm import get_llm


class BasePipeline:
    prompt_template: str = ""
    output_format: str = "text"

    def _build_context(self, docs: list[Document]) -> str:
        parts = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "N/A")
            parts.append(f"[{i}] ({source} p.{page})\n{doc.page_content}")
        return "\n\n".join(parts)

    def run(self, question: str, docs: list[Document]) -> dict:
        llm = get_llm()
        context = self._build_context(docs)
        prompt = ChatPromptTemplate.from_messages(
            [("human", self.prompt_template)]
        )
        chain = prompt | llm
        resp = chain.invoke({"question": question, "context": context})
        return self._parse_output(resp.content)

    def _parse_output(self, content: str) -> dict:
        return {"answer": content, "structured": None}

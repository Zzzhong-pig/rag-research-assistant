"""Tool 5: Citation 引用生成"""

from langchain_core.documents import Document

from app.tools.base import BaseTool
from app.utils import format_sources


class CitationTool(BaseTool):
    name = "citation"
    description = "基于检索文档生成标准化引用列表"

    def run(self, docs: list[Document] | None = None, answer: str = "", **_) -> dict:
        docs = docs or []
        citations = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", "N/A")
            title = str(source).split("/")[-1].replace(".pdf", "")
            citations.append(
                {
                    "id": i,
                    "marker": f"[{i}]",
                    "title": title,
                    "source": source,
                    "page": page,
                    "snippet": doc.page_content[:150] + "...",
                }
            )

        bibtex_lines = []
        for c in citations:
            key = c["title"].replace(" ", "_")[:30]
            bibtex_lines.append(
                f"@article{{{key},\n  title={{{c['title']}}},\n  note={{page {c['page']}}}\n}}"
            )

        return {
            "citations": citations,
            "sources": format_sources(docs),
            "bibtex": "\n\n".join(bibtex_lines),
            "inline_refs": " ".join(c["marker"] for c in citations),
            "answer_with_refs": answer,
        }
